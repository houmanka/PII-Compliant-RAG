from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine, OperatorConfig
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("PII_CLASSIFY")
analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

@mcp.tool()
async def pii_classify(text: str) -> dict:
    analyzer_results = analyzer.analyze(text=text, language='en')
    entities = []

    if analyzer_results:
        anonymized_result = anonymizer.anonymize(
            text=text,
            analyzer_results=analyzer_results,
            operators={"DEFAULT": OperatorConfig("redact", {})}
        )
        for result in analyzer_results:
            entities.append({
                "start": result.start,
                "end": result.end,
                "score": result.score,
                "entity": result.entity_type,
            })

        return {"redacted_text": anonymized_result.text, "entities": entities}
    else:
        return {"redacted_text": text, "entities": entities}


def main():
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()