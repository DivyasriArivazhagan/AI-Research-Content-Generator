
import os
import json
import time

from dotenv import load_dotenv
from google import genai

from backend.rag_pipeline import retrieve_relevant_chunks


# ========================================
# GEMINI CONFIGURATION
# ========================================

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file")

client = genai.Client(api_key=api_key)

MODEL_NAME = "gemini-3.5-flash-lite"

MAX_RETRIES = 3
RETRY_DELAY = 2


# ========================================
# GEMINI API RETRY HANDLER
# ========================================

def generate_with_retry(prompt, config=None):

    for attempt in range(MAX_RETRIES):

        try:
            request_options = {
                "model": MODEL_NAME,
                "contents": prompt
            }

            if config:
                request_options["config"] = config

            response = client.models.generate_content(
                **request_options
            )

            return response

        except Exception as error:

            error_message = str(error).lower()

            temporary_errors = [
                "503",
                "unavailable",
                "500",
                "502",
                "504",
                "429",
                "resource_exhausted"
            ]

            is_temporary = any(
                code in error_message
                for code in temporary_errors
            )

            if is_temporary and attempt < MAX_RETRIES - 1:

                wait_time = RETRY_DELAY * (2 ** attempt)

                print(
                    f"Gemini temporary error. "
                    f"Retrying in {wait_time} seconds... "
                    f"Attempt {attempt + 2}/{MAX_RETRIES}"
                )

                time.sleep(wait_time)

            else:
                raise error


# ========================================
# 1. RESEARCH AGENT
# ========================================

def research_agent(topic):

    if not topic or not topic.strip():
        return {
            "status": "error",
            "message": "Research topic is required"
        }

    results = retrieve_relevant_chunks(topic, n_results=5)

    if not results:
        return {
            "status": "error",
            "message": "No relevant research information found"
        }

    return {
        "status": "success",
        "topic": topic,
        "results": results
    }


# ========================================
# 2. RETRIEVAL AGENT
# ========================================

def retrieval_agent(topic):

    research_data = research_agent(topic)

    if research_data["status"] != "success":
        return research_data

    information = []

    for item in research_data["results"]:

        information.append({
            "source": item["source"],
            "chunk_number": item["chunk_number"],
            "content": item["text"]
        })

    return {
        "status": "success",
        "retrieved_information": information
    }


# ========================================
# 3. WRITER AGENT
# ========================================

def writer_agent(topic, content_type, retrieved_information):

    if not retrieved_information:
        return {
            "status": "error",
            "message": "No research information available"
        }

    research_context = ""

    for index, item in enumerate(retrieved_information, start=1):

        research_context += f"""
SOURCE {index}

Filename: {item['source']}

Chunk: {item['chunk_number']}

Content:
{item['content']}

"""

    prompt = f"""
You are an academic research content writing assistant.

RESEARCH TOPIC:
{topic}

CONTENT TYPE:
{content_type}

SOURCE MATERIAL:
{research_context}

INSTRUCTIONS:

1. Generate a well-structured {content_type}.
2. Use the supplied research information as the factual basis.
3. Do not invent facts, statistics or references.
4. Do not claim information is in the sources if it is not.
5. Use clear professional English.
6. Include a suitable title and headings where appropriate.
7. Add a Sources section.
8. Mention source filenames and chunk numbers.
9. If the sources are insufficient, clearly mention the limitation.

Generate the complete content now.
"""

    try:

        response = generate_with_retry(prompt)

        generated_content = response.text

        if not generated_content:
            raise ValueError("Gemini returned an empty response")

        return {
            "status": "success",
            "topic": topic,
            "content_type": content_type,
            "generated_content": generated_content,
            "sources": retrieved_information
        }

    except Exception as error:

        return {
            "status": "error",
            "message": str(error)
        }


# ========================================
# 4. VERIFICATION AGENT
# ========================================

def verification_agent(generated_content, retrieved_information):

    if not generated_content or not retrieved_information:

        return {
            "status": "error",
            "message": "Content or source information is missing"
        }

    source_context = ""

    for index, item in enumerate(retrieved_information, start=1):

        source_context += f"""
SOURCE {index}

Filename: {item['source']}

Chunk Number: {item['chunk_number']}

Source Content:
{item['content']}

"""

    verification_prompt = f"""
You are a research content verification agent.

Your task is to verify the generated content using ONLY the
provided research source material.

GENERATED CONTENT:
{generated_content}

ORIGINAL RESEARCH SOURCES:
{source_context}

VERIFICATION INSTRUCTIONS:

1. Check whether factual claims are supported by the sources.
2. Identify claims that are unsupported by the sources.
3. Identify any statements that contradict the source material.
4. Do not treat opinions or general writing style as factual errors.
5. Do not invent corrections or additional facts.
6. If evidence is insufficient, clearly state that.
7. Do not assume a claim is verified merely because it sounds correct.

Return ONLY valid JSON in this format:

{{
    "overall_status": "Verified, Partially Verified, or Needs Review",
    "verified_claims": [],
    "unsupported_claims": [],
    "contradictions": [],
    "suggested_corrections": [],
    "summary": "Short explanation of the verification result"
}}
"""

    try:

        response = generate_with_retry(
            verification_prompt,
            config={
                "response_mime_type": "application/json"
            }
        )

        if not response.text:
            raise ValueError("Gemini returned an empty verification response")

        verification_result = json.loads(response.text)

        required_fields = [
            "overall_status",
            "verified_claims",
            "unsupported_claims",
            "contradictions",
            "suggested_corrections",
            "summary"
        ]

        for field in required_fields:
            if field not in verification_result:
                raise ValueError(
                    f"Verification response missing field: {field}"
                )

        return {
            "status": "success",
            "verification": verification_result
        }

    except Exception as error:

        print("Verification Agent Error:", str(error))

        return {
            "status": "error",
            "message": str(error)
        }


# ========================================
# 5. COMPLETE AGENT WORKFLOW
# ========================================

def run_agent_workflow(topic, content_type):

    # Step 1: Research and retrieve information

    retrieval_result = retrieval_agent(topic)

    if retrieval_result["status"] != "success":
        return retrieval_result

    retrieved_information = retrieval_result["retrieved_information"]

    # Step 2: Generate content

    writer_result = writer_agent(
        topic,
        content_type,
        retrieved_information
    )

    if writer_result["status"] != "success":
        return writer_result

    generated_content = writer_result["generated_content"]

    # Step 3: Verify generated content

    verification_result = verification_agent(
        generated_content,
        retrieved_information
    )

    if verification_result["status"] == "success":

        verification_data = verification_result["verification"]

    else:

        verification_data = {
            "overall_status": "Verification Unavailable",
            "verified_claims": [],
            "unsupported_claims": [],
            "contradictions": [],
            "suggested_corrections": [],
            "summary": verification_result["message"]
        }

    return {
        "status": "success",
        "topic": topic,
        "content_type": content_type,
        "generated_content": generated_content,
        "sources": retrieved_information,
        "verification": verification_data
    }
