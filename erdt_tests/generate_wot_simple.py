"""
Quick script to generate WoT TD - run with: python -m generate_wot_simple
"""
if __name__ == "__main__":
    import json
    from models.industries.logistics import create_logistics_model
    from transformation.erdt_to_wot import transform_erdt_to_wot
    
    # Create and transform
    model = create_logistics_model()
    wot_td = transform_erdt_to_wot(model)
    
    # Save and print
    with open('logistics_wot_td.json', 'w') as f:
        json.dump(wot_td, f, indent=2)
    
    print(json.dumps(wot_td, indent=2))
    print("\n✓ Saved to logistics_wot_td.json")
