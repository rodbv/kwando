import pandas as pd
import random

# Tag probabilities
APP_PROB = 0.95
SUPPORT_PROB = 0.20
URGENT_PROB = 0.20
QUICKWIN_PROB = 0.10

TAG_ORDER = ["app", "support", "urgent", "quickwin"]


def assign_tags():
    tags = []
    # 'app' tag
    if random.random() < APP_PROB:
        tags.append("app")
    # Other tags, independently
    if random.random() < SUPPORT_PROB:
        tags.append("support")
    if random.random() < URGENT_PROB:
        tags.append("urgent")
    if random.random() < QUICKWIN_PROB:
        tags.append("quickwin")
    return ",".join(tags)


def add_tags_to_csv(input_file, output_file):
    """Add a tags column to a CSV file with random tag assignments (comma-separated)."""
    df = pd.read_csv(input_file)
    tags_list = [assign_tags() for _ in range(len(df))]
    df["tags"] = tags_list
    df.to_csv(output_file, index=False)
    print(f"Added tags to {input_file} -> {output_file}")
    # Print tag statistics
    tag_counts = {tag: 0 for tag in TAG_ORDER}
    tag_counts["(no tags)"] = 0
    for tags in tags_list:
        if not tags:
            tag_counts["(no tags)"] += 1
        else:
            for tag in tags.split(","):
                tag_counts[tag] += 1
    total = len(tags_list)
    print("Tag distribution:")
    for tag in TAG_ORDER + ["(no tags)"]:
        count = tag_counts[tag]
        print(f"  {tag}: {count} ({count/total*100:.1f}%)")


if __name__ == "__main__":
    add_tags_to_csv("data/data.csv", "data/data_with_tags.csv")
    add_tags_to_csv("data/data2.csv", "data/data2_with_tags.csv")
