def __init__(self, mapping_path: str, model_dir: str = None):
    mapping_file = Path(mapping_path)
    print(f"🔍 Loading mapping from {mapping_file.resolve()}")
    with mapping_file.open('r') as f:
        mapping_data = json.load(f)
    print(f"✔️  Loaded {sum(len(d) for d in mapping_data.values())} standard terms")
