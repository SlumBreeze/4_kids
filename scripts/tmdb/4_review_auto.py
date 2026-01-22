from datetime import datetime, timezone
from shared.io_utils import load_json, save_json
from shared.models import AssessedItem, ReviewedItem
from shared.config import ASSESSED_FILE, REVIEWED_FILE

def main():
    print("Starting automated review...")
    # Load data
    assessed_data = load_json(ASSESSED_FILE)
    if not assessed_data:
        print("No assessed items found.")
        return

    assessed_items = [AssessedItem.from_dict(item) for item in assessed_data]

    reviewed_data = load_json(REVIEWED_FILE) or []
    reviewed_ids = {item['enriched']['tmdb_id'] for item in reviewed_data}

    pending = [item for item in assessed_items if item.enriched.tmdb_id not in reviewed_ids]

    if not pending:
        print("No pending items to review.")
        return

    print(f"Found {len(pending)} pending items.")
    newly_reviewed = []

    for item in pending:
        ai = item.assessment

        # Logic: max_age 99 becomes 18
        final_max_age = ai.max_age
        if final_max_age >= 99:
            final_max_age = 18.0

        # Replicate tag logic from 4_review.py (Accept action)
        tags = []
        if ai.is_educational:
            tags.append("Educational")
        if ai.has_lgbtq:
            tags.append("LGBTQ+ Themes")
        if ai.has_violence:
            tags.append("Violence")
        if ai.has_scary:
            tags.append("Scary Imagery")

        # Create ReviewedItem
        reviewed_item = ReviewedItem(
            enriched=item.enriched,
            rating=ai.rating,
            tags=tags,
            reasoning=ai.reasoning,
            min_age=ai.min_age,
            max_age=final_max_age,
            stimulation_level=ai.stimulation_level,
            featured=False,
            ai_suggestion=ai,
            reviewed_at=datetime.now(timezone.utc).isoformat()
        )

        newly_reviewed.append(reviewed_item.to_dict())

    # Save
    all_reviewed = reviewed_data + newly_reviewed
    save_json(REVIEWED_FILE, all_reviewed)
    print(f"Successfully reviewed {len(newly_reviewed)} items. Total reviewed: {len(all_reviewed)}")

if __name__ == "__main__":
    main()
