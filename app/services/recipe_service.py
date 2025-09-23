import pandas as pd
from dotenv import load_dotenv
import os

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

# Retriever를 담을 전역 변수 (메모리에 한 번만 로드하기 위함)
RETRIEVER = None


# -----------------------------------------------------
# 1. 데이터 로딩 및 전처리 함수
# -----------------------------------------------------
def load_and_process_data(file_path: str) -> list[Document]:
    """CSV 파일을 읽어 LangChain Document 객체 리스트로 변환하고, 메타데이터를 강화합니다."""
    print(f"'{file_path}'에서 데이터를 로딩합니다...")
    df = pd.read_csv(file_path)

    # 컬럼명 변경
    df = df.rename(
        columns={
            "RECIPE_NM_KO": "title",
            "SUMRY": "summary",
            "IRDNT_NM": "ingredient_name",
            "IRDNT_CPCTY": "ingredient_amount",
            "COOKING_DC": "instruction",
        }
    )

    documents = []
    for recipe_id, group in df.groupby("RECIPE_ID"):
        # 그룹에서 유효한 값 추출
        title = (
            group["title"].dropna().iloc[0]
            if not group["title"].dropna().empty
            else "제목 없음"
        )
        summary = (
            group["summary"].dropna().iloc[0]
            if not group["summary"].dropna().empty
            else "요약 없음"
        )

        # 재료 정보 합치기 및 리스트 생성
        ingredients_df = group.dropna(subset=["ingredient_name", "ingredient_amount"])
        ingredients_text = ", ".join(
            ingredients_df.apply(
                lambda x: f"{x['ingredient_name']} {x['ingredient_amount']}", axis=1
            )
        )
        # metadata에 저장할 순수 재료 이름 리스트
        ingredient_list = ingredients_df["ingredient_name"].unique().tolist()

        # 조리 과정 정보 합치기 (순서대로 정렬)
        instructions = group.dropna(subset=["instruction", "COOKING_NO"]).sort_values(
            "COOKING_NO"
        )
        instructions_text = "\n".join(
            instructions.apply(
                lambda x: f"{int(x['COOKING_NO'])}. {x['instruction']}", axis=1
            )
        )

        # 최종 Document 내용 구성
        content = f"""
요리명: {title}

요약: {summary}

[재료]
{ingredients_text}

[조리 방법]
{instructions_text}
"""
        # metadata에 'ingredients' 키로 재료 리스트 추가
        metadata = {
            "source": title,
            "recipe_id": int(recipe_id),
            "title": title,
            "ingredients": ingredient_list,
        }
        documents.append(Document(page_content=content.strip(), metadata=metadata))

    print(f"✅ Document 객체 {len(documents)}개 생성 완료 (메타데이터 강화)")
    return documents


# -----------------------------------------------------
# 2. 벡터 데이터베이스 생성 함수
# -----------------------------------------------------
def create_vector_store(documents: list[Document]):
    """Document 리스트를 받아 FAISS 벡터 DB를 생성하고 Retriever를 반환합니다."""
    print("텍스트를 청크로 분할합니다...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000, chunk_overlap=200, length_function=len
    )
    chunks = text_splitter.split_documents(documents)
    print(f"총 {len(chunks)}개의 청크로 분할되었습니다.")

    print(
        "OpenAI 임베딩을 사용하여 벡터 DB를 생성합니다. 시간이 다소 걸릴 수 있습니다..."
    )
    embeddings = OpenAIEmbeddings()

    # FAISS DB를 배치 단위로 생성하여 메모리 및 API 호출 부담 감소
    batch_size = 100
    # 청크가 하나도 없는 경우를 대비한 예외 처리
    if not chunks:
        print("경고: 분할된 청크가 없어 벡터 DB를 생성할 수 없습니다.")
        return None

    vec_db = FAISS.from_documents(chunks[:batch_size], embeddings)
    for i in range(batch_size, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        vec_db.add_documents(batch)
        print(f"{i + len(batch)}/{len(chunks)} 처리 완료...")

    print("✅ 벡터 DB 생성 완료!")
    return vec_db


# -----------------------------------------------------
# 3. Retriever 초기화 함수
# -----------------------------------------------------
FAISS_INDEX_PATH = "./data/faiss_index"


def initialize_retriever():
    global RETRIEVER
    if RETRIEVER is None:
        print("Retriever 초기화를 시작합니다...")
        load_dotenv()
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError(
                "OPENAI_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요."
            )
        embeddings = OpenAIEmbeddings()

        if os.path.exists(FAISS_INDEX_PATH):
            print("저장된 벡터 DB를 불러옵니다...")
            vec_db = FAISS.load_local(
                FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True
            )
            RETRIEVER = vec_db.as_retriever()

        else:
            print(f"새로운 벡터DB를 생성하고 저장합니다...")
            documents = load_and_process_data("./data/recipes_all.csv")

            vec_db = create_vector_store(documents)

            vec_db.save_local(FAISS_INDEX_PATH)
            print(f"'{FAISS_INDEX_PATH}'에 벡터 DB를 저장했습니다.")

            RETRIEVER = vec_db.as_retriever()

        print(" Retriever 초기화 완료!")


# -----------------------------------------------------
# 4. 레시피 추천 서비스 함수
# -----------------------------------------------------
def recommend_recipes_by_ingredients(
    ingredients: list[str], top_k: int = 3
) -> list[dict]:
    """
    재료 리스트를 받아 가장 관련성 높은 레시피 N개를 필터링하여 반환합니다.
    """
    if RETRIEVER is None:
        initialize_retriever()

    # 1. 재료들을 합쳐서 검색 쿼리 생성
    query = ", ".join(ingredients)
    print(f"검색 쿼리: {query}")

    # 2. 유사도 기반으로 관련 레시피 문서 검색 (일단 넓게 10개 정도)
    retrieved_docs = RETRIEVER.get_relevant_documents(query, k=10)

    # 3. 검색된 문서들 중에서, 입력된 모든 재료를 포함하는 레시피만 필터링
    final_recipes = []
    found_ids = set()  # 중복 추천 방지

    for doc in retrieved_docs:
        # metadata에 저장된 재료 리스트를 가져옴
        doc_ingredients = doc.metadata.get("ingredients", [])

        # 입력된 모든 재료가 레시피의 재료 목록에 포함되는지 확인
        # (대소문자 구분 없이 비교)
        if all(
            req_ing.lower() in [s.lower() for s in doc_ingredients]
            for req_ing in ingredients
        ):
            recipe_id = doc.metadata.get("recipe_id")
            if recipe_id not in found_ids:
                # 웹으로 보낼 최종 정보 구성
                final_recipes.append(
                    {
                        "title": doc.metadata.get("title", ""),
                        "summary": doc.page_content.split("요약:")[1]
                        .split("[재료]")[0]
                        .strip(),
                        "recipe_id": recipe_id,
                        "ingredients": doc_ingredients,
                        "full_recipe": doc.page_content,  # 레시피 전체 내용도 추가
                    }
                )
                found_ids.add(recipe_id)

    # 4. 최종 결과에서 상위 N개만 반환
    return final_recipes[:top_k]
