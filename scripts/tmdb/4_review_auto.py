import argparse
from datetime import datetime, timezone
from shared.io_utils import load_json, save_json
from shared.models import AssessedItem, ReviewedItem
from shared.config import ASSESSED_FILE, REVIEWED_FILE

def reviewed_from_assessed(item):
    assessment = item.assessment
    final_min_age = min(float(assessment.min_age), 5.0)
    final_max_age = min(float(assessment.max_age), 5.0)
    if final_min_age > final_max_age:
        final_min_age = final_max_age

    tags = []
    if assessment.is_educational:
        tags.append("Educational")
    if assessment.has_lgbtq:
        tags.append("LGBTQ+ Themes")
    if assessment.has_violence:
        tags.append("Violence")
    if assessment.has_scary:
        tags.append("Scary Imagery")

    reviewed_item = ReviewedItem(
        enriched=item.enriched,
        rating=assessment.rating,
        tags=tags,
        reasoning=assessment.reasoning,
        min_age=final_min_age,
        max_age=final_max_age,
        stimulation_level=assessment.stimulation_level,
        featured=False,
        safe_above_age=assessment.safe_above_age,
        is_episodic_issue=assessment.is_episodic_issue,
        ai_suggestion=assessment,
        reviewed_at=datetime.now(timezone.utc).isoformat()
    )

    return reviewed_item.to_dict()

def main():
    parser = argparse.ArgumentParser(description="Automatically accept assessed items into reviewed staging.")
    parser.add_argument(
        "--append",
        action="store_true",
        help="Only append assessed items that are not already reviewed. Default rebuilds reviewed staging.",
    )
    args = parser.parse_args()

    print("Starting automated review...")
    # Load data
    assessed_data = load_json(ASSESSED_FILE)
    if not assessed_data:
        print("No assessed items found.")
        return

    assessed_items = [AssessedItem.from_dict(item) for item in assessed_data]

    if not args.append:
        reviewed_data = [reviewed_from_assessed(item) for item in assessed_items]
        save_json(REVIEWED_FILE, reviewed_data)
        print(f"Rebuilt reviewed staging from {len(reviewed_data)} assessed items.")
        return

    reviewed_data = load_json(REVIEWED_FILE) or []
    reviewed_ids = {item['enriched']['tmdb_id'] for item in reviewed_data}
    pending = [item for item in assessed_items if item.enriched.tmdb_id not in reviewed_ids]

    if not pending:
        print("No pending items to review.")
        return

    print(f"Found {len(pending)} pending items.")
    newly_reviewed = [reviewed_from_assessed(item) for item in pending]

    # Save
    all_reviewed = reviewed_data + newly_reviewed
    save_json(REVIEWED_FILE, all_reviewed)
    print(f"Successfully reviewed {len(newly_reviewed)} items. Total reviewed: {len(all_reviewed)}")

if __name__ == "__main__":
    main()
