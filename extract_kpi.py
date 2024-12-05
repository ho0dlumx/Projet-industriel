#!/usr/bin/env python3

import argparse
import csv
import logging
from pathlib import Path
from private_gpt.di import global_injector
from private_gpt.server.ingest.ingest_service import IngestService
from private_gpt.settings.settings import Settings
from private_gpt.server.chat.chat_service import ChatService

# Logging configuration
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s")

# KPI dictionary with prompts for extraction
kpi_prompts = {
    "CO2 Consumption": "What was the total CO2 consumption during this period? (Return only the value as an integer)",
    "Greenhouse Gas Emissions": "What were the total greenhouse gas emissions reported? (Provide the amount in tons)",
    "Renewable Energy Usage": "What percentage of energy used came from renewable sources? (Return only the percentage as a number)",
    "Employee Training Hours": "How many training hours were provided to employees during this period? (Return only the total number of hours)",
    "Ethical Non-Compliance Cases": "How many cases of ethical non-compliance were reported? (Return the number as an integer)",
    "Social Investments": "What was the total investment in social initiatives during this period? (Provide the amount in local currency)",
    "Employee Turnover Rate": "What was the employee turnover rate during this period? (Return as a percentage)",
    "Corruption Incidents": "How many incidents of corruption were detected or reported? (Provide as an integer)"
}


class KPIExtractor:
    def __init__(self, ingest_service: IngestService, chat_service: ChatService, settings: Settings):
        self.ingest_service = ingest_service
        self.chat_service = chat_service
        self.settings = settings

    def ingest_files(self, folder_path: Path):
        """Ingest files directly from the specified folder."""
        try:
            logger.info(f"Starting ingestion for folder: {folder_path}")
            files_to_ingest = [(f.name, f) for f in folder_path.iterdir() if f.is_file() and f.suffix.lower() == ".pdf"]
            self.ingest_service.bulk_ingest(files_to_ingest)
            logger.info(f"Successfully ingested {len(files_to_ingest)} documents from {folder_path}")
        except Exception as e:
            logger.error(f"Failed to ingest documents from {folder_path}: {e}")
            raise

    def wipe_index(self):
        """Wipe the current index."""
        try:
            logger.info("Wiping the current index...")
            self.ingest_service.wipe()
            logger.info("Index wiped successfully.")
        except Exception as e:
            logger.error(f"Failed to wipe index: {e}")
            raise

    def extract_kpi(self, kpi_name: str) -> str:
        """Extract the value for a specific KPI using ChatService."""
        if kpi_name not in kpi_prompts:
            raise ValueError(f"KPI '{kpi_name}' not found in dictionary.")
        prompt = kpi_prompts[kpi_name]
        try:
            logger.info(f"Extracting KPI '{kpi_name}' with prompt: {prompt}")
            response = self.chat_service.chat(prompt)
            return response.strip()
        except Exception as e:
            logger.error(f"Failed to extract KPI '{kpi_name}': {e}")
            raise


def main():
    parser = argparse.ArgumentParser(description="Extract KPIs from PDF documents.")
    parser.add_argument("folder", help="Folder containing PDF documents for KPI extraction")
    parser.add_argument("--output", help="Output CSV file to store extracted KPIs", default="kpi_results.csv")
    parser.add_argument("--log-file", help="Optional log file path", default=None)
    args = parser.parse_args()

    if args.log_file:
        file_handler = logging.FileHandler(args.log_file)
        file_handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s"))
        logger.addHandler(file_handler)

    folder_path = Path(args.folder)
    if not folder_path.exists():
        raise ValueError(f"Folder {args.folder} does not exist.")
    if not folder_path.is_dir():
        raise ValueError(f"Path {args.folder} is not a folder.")

    # Initialize services
    ingest_service = global_injector.get(IngestService)
    chat_service = global_injector.get(ChatService)  # Retrieve the ChatService singleton
    settings = global_injector.get(Settings)
    extractor = KPIExtractor(ingest_service, chat_service, settings)

    results = []
    try:
        # Ingest files from the specified folder
        extractor.ingest_files(folder_path)

        # Extract KPIs from each file
        for kpi_name in kpi_prompts.keys():
            try:
                value = extractor.extract_kpi(kpi_name)
                results.append({
                    "KPI": kpi_name,
                    "Value": value
                })
                logger.info(f"KPI extracted: {kpi_name} -> {value}")
            except Exception as e:
                logger.warning(f"Failed to extract KPI '{kpi_name}': {e}")

        # Wipe the index after extraction
        extractor.wipe_index()
    except Exception as e:
        logger.error(f"Error during processing: {e}")

    # Write results to a CSV file
    output_file = Path(args.output)
    try:
        with output_file.open(mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=["KPI", "Value"])
            writer.writeheader()
            writer.writerows(results)
        logger.info(f"Results written to {output_file}")
    except Exception as e:
        logger.error(f"Failed to write results to {output_file}: {e}")


if __name__ == "__main__":
    main()
