import csv
import json
import re
import os
from pathlib import Path

# ===================================================================
# CONFIGURATION SECTION - Modify these according to your needs
# ===================================================================

# MULTIPLE INPUT FILES CONFIGURATION
# Option 1: List all input files explicitly
INPUT_FILES = [
    {
        'path': 'input_food_data_1.csv',
        'source': '#1food-moz.pdf',
        'category_override': None,  # None = auto-detect, or specify category
        'enabled': True
    },
    {
        'path': 'input_food_data_2.csv',
        'source': '#2nutrition-database.pdf',
        'category_override': None,
        'enabled': True
    },
    {
        'path': 'input_food_data_3.csv',
        'source': '#3regional-foods.pdf',
        'category_override': None,
        'enabled': False
    }
]

# Option 2: Process all CSV files in a directory
USE_DIRECTORY_MODE = False  # Set to True to use directory mode
INPUT_DIRECTORY = 'input_datasets'  # Directory containing CSV files
OUTPUT_DIRECTORY = 'output_datasets'  # Directory for output files

# Single output file or separate files?
MERGE_OUTPUT = True  # True = one combined file, False = separate files per input
OUTPUT_FILE = 'combined_food_data.csv'  # Used only if MERGE_OUTPUT = True

# Conflict resolution for duplicate food IDs across datasets
CONFLICT_RESOLUTION = 'suffix'  # Options: 'suffix', 'skip', 'overwrite', 'merge'
# - suffix: Add source suffix to duplicate IDs (e.g., arroz_1, arroz_2)
# - skip: Skip duplicate entries from later datasets
# - overwrite: Later datasets overwrite earlier ones
# - merge: Attempt to merge nutritional data (average values)

# Default values
DEFAULT_CATEGORY = 'Alimentos'
DEFAULT_PAGE = '1'

# ===================================================================
# UNIT CONVERSIONS DATABASE (Same as before)
# ===================================================================

UNIT_CONVERSIONS_DATABASE = {
    'cereais': {
        'defaultUnit': '100g',
        'units': ["100g", "gramas", "g", "xícara", "xícara de chá", "colher de sopa", "colher de chá", "kg"],
        'conversions': {
            "100g": 100, "gramas": 1, "g": 1, "xícara": 200,
            "xícara de chá": 200, "colher de sopa": 15, "colher de chá": 5, "kg": 1000
        }
    },
    'arroz': {
        'defaultUnit': '100g',
        'units': ["100g", "gramas", "g", "xícara", "xícara de chá", "colher de sopa", "colher de chá", "prato fundo", "prato raso", "concha", "kg"],
        'conversions': {
            "100g": 100, "gramas": 1, "g": 1, "xícara": 200, "xícara de chá": 200,
            "colher de sopa": 15, "colher de chá": 5, "prato fundo": 300, "prato raso": 150, "concha": 120, "kg": 1000
        }
    },
    'leguminosas': {
        'defaultUnit': '100g',
        'units': ["100g", "gramas", "g", "xícara", "colher de sopa", "concha", "prato fundo", "kg"],
        'conversions': {
            "100g": 100, "gramas": 1, "g": 1, "xícara": 180,
            "colher de sopa": 12, "concha": 100, "prato fundo": 250, "kg": 1000
        }
    },
    'carnes': {
        'defaultUnit': '100g',
        'units': ["100g", "gramas", "g", "bife", "filé", "peito", "coxa", "sobrecoxa", "fatia", "porção", "kg"],
        'conversions': {
            "100g": 100, "gramas": 1, "g": 1, "bife": 120, "filé": 150,
            "peito": 200, "coxa": 150, "sobrecoxa": 180, "fatia": 30, "porção": 150, "kg": 1000
        }
    },
    'peixes': {
        'defaultUnit': '100g',
        'units': ["100g", "gramas", "g", "filé", "posta", "unidade", "porção", "kg"],
        'conversions': {
            "100g": 100, "gramas": 1, "g": 1, "filé": 150,
            "posta": 200, "unidade": 180, "porção": 150, "kg": 1000
        }
    },
    'laticínios': {
        'defaultUnit': '100g',
        'units': ["100g", "gramas", "g", "ml", "litro", "copo", "xícara", "colher de sopa", "colher de chá", "fatia"],
        'conversions': {
            "100g": 100, "gramas": 1, "g": 1, "ml": 1.03, "litro": 1030,
            "copo": 240, "xícara": 240, "colher de sopa": 15, "colher de chá": 5, "fatia": 20
        }
    },
    'frutas': {
        'defaultUnit': '100g',
        'units': ["100g", "gramas", "g", "unidade", "unidade pequena", "unidade média", "unidade grande", "fatia", "rodela", "xícara", "colher de sopa", "kg"],
        'conversions': {
            "100g": 100, "gramas": 1, "g": 1, "unidade": 150, "unidade pequena": 100,
            "unidade média": 150, "unidade grande": 200, "fatia": 50, "rodela": 30, "xícara": 120, "colher de sopa": 15, "kg": 1000
        }
    },
    'vegetais': {
        'defaultUnit': '100g',
        'units': ["100g", "gramas", "g", "unidade", "xícara", "colher de sopa", "colher de chá", "prato fundo", "prato raso", "folha", "kg"],
        'conversions': {
            "100g": 100, "gramas": 1, "g": 1, "unidade": 120, "xícara": 100,
            "colher de sopa": 10, "colher de chá": 3, "prato fundo": 200, "prato raso": 100, "folha": 10, "kg": 1000
        }
    },
    'tubérculos': {
        'defaultUnit': '100g',
        'units': ["100g", "gramas", "g", "unidade", "unidade pequena", "unidade média", "unidade grande", "fatia", "pedaço", "xícara", "kg"],
        'conversions': {
            "100g": 100, "gramas": 1, "g": 1, "unidade": 180, "unidade pequena": 120,
            "unidade média": 180, "unidade grande": 250, "fatia": 40, "pedaço": 50, "xícara": 150, "kg": 1000
        }
    },
    'óleos': {
        'defaultUnit': '100g',
        'units': ["100g", "gramas", "g", "ml", "litro", "colher de sopa", "colher de chá", "fio"],
        'conversions': {
            "100g": 100, "gramas": 1, "g": 1, "ml": 0.92, "litro": 920,
            "colher de sopa": 13, "colher de chá": 4, "fio": 2
        }
    },
    'açúcares': {
        'defaultUnit': '100g',
        'units': ["100g", "gramas", "g", "colher de sopa", "colher de chá", "xícara", "kg"],
        'conversions': {
            "100g": 100, "gramas": 1, "g": 1, "colher de sopa": 12,
            "colher de chá": 4, "xícara": 180, "kg": 1000
        }
    },
    'bebidas': {
        'defaultUnit': '100ml',
        'units': ["100ml", "ml", "litro", "copo", "xícara", "colher de sopa", "colher de chá"],
        'conversions': {
            "100ml": 100, "ml": 1, "litro": 1000, "copo": 240,
            "xícara": 240, "colher de sopa": 15, "colher de chá": 5
        }
    },
    'ovos': {
        'defaultUnit': '100g',
        'units': ["100g", "gramas", "g", "unidade", "unidade pequena", "unidade média", "unidade grande", "clara", "gema"],
        'conversions': {
            "100g": 100, "gramas": 1, "g": 1, "unidade": 50, "unidade pequena": 40,
            "unidade média": 50, "unidade grande": 60, "clara": 30, "gema": 20
        }
    },
    'pães': {
        'defaultUnit': '100g',
        'units': ["100g", "gramas", "g", "unidade", "fatia", "fatia fina", "fatia grossa", "pão francês", "pãozinho", "xícara", "kg"],
        'conversions': {
            "100g": 100, "gramas": 1, "g": 1, "unidade": 50, "fatia": 25,
            "fatia fina": 20, "fatia grossa": 35, "pão francês": 50, "pãozinho": 50, "xícara": 100, "kg": 1000
        }
    },
    'nozes': {
        'defaultUnit': '100g',
        'units': ["100g", "gramas", "g", "unidade", "xícara", "colher de sopa", "colher de chá", "punhado", "kg"],
        'conversions': {
            "100g": 100, "gramas": 1, "g": 1, "unidade": 5, "xícara": 140,
            "colher de sopa": 10, "colher de chá": 3, "punhado": 30, "kg": 1000
        }
    },
    'default': {
        'defaultUnit': '100g',
        'units': ["100g", "gramas", "g", "unidade", "porção", "colher de sopa", "colher de chá", "xícara", "kg"],
        'conversions': {
            "100g": 100, "gramas": 1, "g": 1, "unidade": 100, "porção": 150,
            "colher de sopa": 15, "colher de chá": 5, "xícara": 150, "kg": 1000
        }
    }
}

# ===================================================================
# MAIN CONVERSION FUNCTIONS
# ===================================================================

def process_multiple_datasets():
    """
    Main function to process multiple input datasets
    """
    print("=" * 70)
    print("Multi-Dataset Food Data Conversion Tool")
    print("=" * 70)
    
    # Determine which input mode to use
    if USE_DIRECTORY_MODE:
        input_configs = discover_input_files()
    else:
        input_configs = [config for config in INPUT_FILES if config['enabled']]
    
    if not input_configs:
        print("✗ No input files configured or found")
        return
    
    print(f"\n📁 Processing {len(input_configs)} dataset(s)...")
    
    # Process each dataset
    all_data = {}  # Dictionary to store all processed data by ID
    dataset_stats = []
    
    for idx, config in enumerate(input_configs, 1):
        print(f"\n{'─' * 70}")
        print(f"Dataset {idx}/{len(input_configs)}: {config['path']}")
        print(f"{'─' * 70}")
        
        try:
            data, stats = process_single_dataset(config, all_data, idx)
            dataset_stats.append(stats)
            
            # Update all_data with new entries
            all_data.update(data)
            
        except FileNotFoundError:
            print(f"✗ File not found: {config['path']}")
            continue
        except Exception as e:
            print(f"✗ Error processing dataset: {str(e)}")
            continue
    
    # Write output
    if all_data:
        write_output(all_data, dataset_stats)
    else:
        print("\n✗ No data was successfully processed")

def discover_input_files():
    """
    Discover all CSV files in the input directory
    """
    input_dir = Path(INPUT_DIRECTORY)
    
    if not input_dir.exists():
        print(f"✗ Input directory not found: {INPUT_DIRECTORY}")
        return []
    
    csv_files = list(input_dir.glob('*.csv'))
    
    configs = []
    for csv_file in csv_files:
        configs.append({
            'path': str(csv_file),
            'source': f'#{csv_file.stem}.pdf',
            'category_override': None,
            'enabled': True
        })
    
    print(f"📂 Discovered {len(configs)} CSV file(s) in {INPUT_DIRECTORY}")
    return configs

def process_single_dataset(config, existing_data, dataset_number):
    """
    Process a single input dataset
    
    Returns:
        Tuple of (processed_data_dict, statistics)
    """
    input_file = config['path']
    source_pdf = config['source']
    category_override = config['category_override']
    
    processed_data = {}
    stats = {
        'file': input_file,
        'total': 0,
        'added': 0,
        'skipped': 0,
        'merged': 0,
        'conflicts': []
    }
    
    with open(input_file, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        
        for row_num, row in enumerate(reader, start=1):
            # Extract food information
            food_name = row['description'].strip().strip('"')
            
            if not food_name:
                continue
            
            stats['total'] += 1
            
            # Generate base ID
            base_id = generate_id_from_name(food_name)
            
            # Check for conflicts with existing data
            final_id, conflict_action = resolve_id_conflict(
                base_id, 
                food_name, 
                existing_data, 
                dataset_number
            )
            
            # Track conflict
            if conflict_action in ['skipped', 'merged']:
                stats[conflict_action] += 1
                if conflict_action == 'skipped':
                    stats['conflicts'].append(f"{food_name} (ID: {base_id})")
                    continue
            else:
                stats['added'] += 1
            
            # Process nutritional data
            row_data = create_output_row(
                final_id,
                food_name,
                row,
                source_pdf,
                category_override,
                row_num,
                dataset_number
            )
            
            # Handle merging if needed
            if conflict_action == 'merged' and final_id in existing_data:
                processed_data[final_id] = merge_nutritional_data(
                    existing_data[final_id],
                    row_data
                )
            else:
                processed_data[final_id] = row_data
    
    # Print statistics
    print(f"✓ Processed {stats['total']} items")
    print(f"  • Added: {stats['added']}")
    if stats['skipped'] > 0:
        print(f"  • Skipped (duplicates): {stats['skipped']}")
    if stats['merged'] > 0:
        print(f"  • Merged: {stats['merged']}")
    
    return processed_data, stats

def resolve_id_conflict(base_id, food_name, existing_data, dataset_number):
    """
    Resolve ID conflicts according to configured strategy
    
    Returns:
        Tuple of (final_id, action) where action is 'added', 'skipped', 'merged', or 'overwritten'
    """
    if base_id not in existing_data:
        return base_id, 'added'
    
    if CONFLICT_RESOLUTION == 'skip':
        return base_id, 'skipped'
    
    elif CONFLICT_RESOLUTION == 'overwrite':
        return base_id, 'overwritten'
    
    elif CONFLICT_RESOLUTION == 'merge':
        return base_id, 'merged'
    
    elif CONFLICT_RESOLUTION == 'suffix':
        # Add dataset number suffix
        new_id = f"{base_id}_ds{dataset_number}"
        counter = 2
        while new_id in existing_data:
            new_id = f"{base_id}_ds{dataset_number}_{counter}"
            counter += 1
        return new_id, 'added'
    
    return base_id, 'added'

def create_output_row(food_id, food_name, source_row, source_pdf, 
                     category_override, row_num, dataset_num):
    """
    Create a complete output row from source data
    """
    # Extract nutritional values
    energy_kcal = safe_float(source_row.get('energy_kcal'))
    protein_g = safe_float(source_row.get('protein_g'))
    fat_g = safe_float(source_row.get('lipids_g'))
    carbs_g = safe_float(source_row.get('carbohydrate_g'))
    fiber_g = safe_float(source_row.get('fiber_g'))
    calcium_mg = safe_float(source_row.get('calcium_mg'))
    iron_mg = safe_float(source_row.get('iron_mg'))
    sodium_mg = safe_float(source_row.get('sodium_mg'))
    
    # Build comprehensive nutrition data
    nutrition_per_100g = {
        "calories": energy_kcal,
        "energy_kj": safe_float(source_row.get('energy_kj')),
        "protein": protein_g,
        "fat": fat_g,
        "carbs": carbs_g,
        "fiber": fiber_g,
        "cholesterol": safe_float(source_row.get('cholesterol_mg')),
        "moisture": safe_float(source_row.get('moisture_pct')),
        "ash": safe_float(source_row.get('ash_g')),
        "calcium": calcium_mg,
        "magnesium": safe_float(source_row.get('magnesium_mg')),
        "manganese": safe_float(source_row.get('manganese_mg')),
        "phosphorus": safe_float(source_row.get('phosphorus_mg')),
        "iron": iron_mg,
        "sodium": sodium_mg,
        "potassium": safe_float(source_row.get('potassium_mg')),
        "copper": safe_float(source_row.get('copper_mg')),
        "zinc": safe_float(source_row.get('zinc_mg')),
        "retinol": safe_float(source_row.get('retinol_mcg')),
        "re": safe_float(source_row.get('re_mcg')),
        "rae": safe_float(source_row.get('rae_mcg')),
        "thiamine": safe_float(source_row.get('thiamine_mg')),
        "riboflavin": safe_float(source_row.get('riboflavin_mg')),
        "pyridoxine": safe_float(source_row.get('pyridoxine_mg')),
        "niacin": safe_float(source_row.get('niacin_mg')),
        "vitamin_c": safe_float(source_row.get('vitamin_c_mg'))
    }
    
    # Remove None values
    nutrition_per_100g = {k: v for k, v in nutrition_per_100g.items() if v is not None}
    
    # Determine category
    category = category_override or categorize_food(food_name)
    unit_config = get_unit_config(food_name, category)
    
    return {
        'id': food_id,
        'name': food_name,
        'portion_g': 100,
        'energy_kcal': format_value(energy_kcal),
        'protein_g': format_value(protein_g),
        'fat_g': format_value(fat_g),
        'carbs_g': format_value(carbs_g),
        'fiber_g': format_value(fiber_g),
        'calcium_mg': format_value(calcium_mg),
        'iron_mg': format_value(iron_mg),
        'sodium_mg': format_value(sodium_mg),
        'defaultUnit': unit_config['defaultUnit'],
        'units': json.dumps(unit_config['units'], ensure_ascii=False),
        'unitConversions': json.dumps(unit_config['conversions'], ensure_ascii=False),
        'nutritionPer100g': json.dumps(nutrition_per_100g, ensure_ascii=False),
        'category': category,
        'source_pdf': source_pdf,
        'page': DEFAULT_PAGE,
        'notes': f'Dataset {dataset_num}, Entry {row_num}'
    }

def merge_nutritional_data(existing_row, new_row):
    """
    Merge nutritional data from two rows (averaging numeric values)
    """
    merged = existing_row.copy()
    
    # Average numeric fields
    numeric_fields = ['energy_kcal', 'protein_g', 'fat_g', 'carbs_g', 
                     'fiber_g', 'calcium_mg', 'iron_mg', 'sodium_mg']
    
    for field in numeric_fields:
        val1 = existing_row.get(field, 'NULL')
        val2 = new_row.get(field, 'NULL')
        
        if val1 != 'NULL' and val2 != 'NULL':
            avg = (float(val1) + float(val2)) / 2
            merged[field] = str(round(avg, 2))
    
    # Merge nutritionPer100g JSON
    try:
        nutrition1 = json.loads(existing_row['nutritionPer100g'])
        nutrition2 = json.loads(new_row['nutritionPer100g'])
        
        merged_nutrition = {}
        all_keys = set(nutrition1.keys()) | set(nutrition2.keys())
        
        for key in all_keys:
            if key in nutrition1 and key in nutrition2:
                merged_nutrition[key] = (nutrition1[key] + nutrition2[key]) / 2
            elif key in nutrition1:
                merged_nutrition[key] = nutrition1[key]
            else:
                merged_nutrition[key] = nutrition2[key]
        
        merged['nutritionPer100g'] = json.dumps(merged_nutrition, ensure_ascii=False)
    except:
        pass
    
    # Update notes
    merged['notes'] = f"{existing_row['notes']} | Merged with: {new_row['notes']}"
    
    return merged

def write_output(all_data, stats):
    """
    Write processed data to output file(s)
    """
    print(f"\n{'=' * 70}")
    print("Writing output...")
    print(f"{'=' * 70}")
    
    fieldnames = [
        'id', 'name', 'portion_g', 'energy_kcal', 'protein_g', 
        'fat_g', 'carbs_g', 'fiber_g', 'calcium_mg', 'iron_mg', 
        'sodium_mg', 'defaultUnit', 'units', 'unitConversions', 
        'nutritionPer100g', 'category', 'source_pdf', 'page', 'notes'
    ]
    
    if MERGE_OUTPUT:
        # Single combined output file
        with open(OUTPUT_FILE, 'w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_data.values())
        
        print(f"✓ Combined output saved to: {OUTPUT_FILE}")
        print(f"✓ Total entries: {len(all_data)}")
    
    else:
        # Separate output files per dataset
        if USE_DIRECTORY_MODE:
            os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)
        
        for stat in stats:
            input_path = Path(stat['file'])
            output_path = f"output_{input_path.stem}.csv"
            
            if USE_DIRECTORY_MODE:
                output_path = os.path.join(OUTPUT_DIRECTORY, f"{input_path.stem}_processed.csv")
            
            # Filter data for this dataset
            dataset_data = {k: v for k, v in all_data.items() 
                          if stat['file'] in v.get('notes', '')}
            
            with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(dataset_data.values())
            
            print(f"✓ Output saved: {output_path} ({len(dataset_data)} entries)")
    
    # Print summary
    print(f"\n{'=' * 70}")
    print("Processing Summary:")
    print(f"{'=' * 70}")
    total_processed = sum(s['total'] for s in stats)
    total_added = sum(s['added'] for s in stats)
    total_skipped = sum(s['skipped'] for s in stats)
    total_merged = sum(s['merged'] for s in stats)
    
    print(f"Total items processed: {total_processed}")
    print(f"Total items added: {total_added}")
    if total_skipped > 0:
        print(f"Total items skipped: {total_skipped}")
    if total_merged > 0:
        print(f"Total items merged: {total_merged}")
    print(f"Final dataset size: {len(all_data)}")

# ===================================================================
# HELPER FUNCTIONS
# ===================================================================

def generate_id_from_name(food_name):
    """Generate snake_case ID from food name"""
    name_lower = food_name.lower()
    name_clean = re.sub(r'[^\w\s]', '', name_lower)
    name_clean = re.sub(r'\s+', '_', name_clean)
    name_clean = re.sub(r'_+', '_', name_clean)
    name_clean = name_clean.strip('_')
    return name_clean if name_clean else 'food_item'

def safe_float(value):
    """Safely convert value to float"""
    if not value or value.upper() in ['NA', 'TR', '']:
        return None
    try:
        return float(value)
    except ValueError:
        return None

def format_value(value):
    """Format value for CSV output"""
    return 'NULL' if value is None else str(value)

def categorize_food(food_name):
    """Categorize food based on keywords"""
    food_lower = food_name.lower()
    
    categories = {
        'Cereais': ['arroz', 'trigo', 'aveia', 'milho', 'centeio', 'cevada', 'quinoa'],
        'Leguminosas': ['feijão', 'ervilha', 'lentilha', 'grão', 'soja', 'amendoim'],
        'Carnes': ['boi', 'vaca', 'frango', 'galinha', 'porco', 'peru', 'pato', 'carne', 'vitela'],
        'Peixes': ['peixe', 'salmão', 'atum', 'sardinha', 'bacalhau', 'camarão', 'lula'],
        'Laticínios': ['leite', 'queijo', 'iogurte', 'manteiga', 'nata', 'requeijão'],
        'Frutas': ['maçã', 'banana', 'laranja', 'uva', 'manga', 'mamão', 'abacaxi', 'melancia', 'morango'],
        'Vegetais': ['tomate', 'alface', 'couve', 'espinafre', 'brócolis', 'repolho', 'pimentão'],
        'Tubérculos': ['batata', 'mandioca', 'inhame', 'cará', 'batata-doce'],
        'Óleos': ['óleo', 'azeite', 'gordura', 'banha'],
        'Açúcares': ['açúcar', 'mel', 'doce', 'melado', 'rapadura'],
        'Bebidas': ['suco', 'refrigerante', 'café', 'chá', 'água', 'vinho', 'cerveja'],
        'Ovos': ['ovo'],
        'Pães': ['pão', 'biscoito', 'bolacha', 'massa', 'macarrão', 'espaguete'],
        'Nozes': ['noz', 'castanha', 'amêndoa', 'avelã', 'pistache', 'semente']
    }
    
    for category, keywords in categories.items():
        if any(keyword in food_lower for keyword in keywords):
            return category
    
    return DEFAULT_CATEGORY

def get_unit_config(food_name, category):
    """Get appropriate unit configuration"""
    food_lower = food_name.lower()
    
    category_map = {
        'Cereais': 'cereais', 'Leguminosas': 'leguminosas', 'Carnes': 'carnes',
        'Peixes': 'peixes', 'Laticínios': 'laticínios', 'Frutas': 'frutas',
        'Vegetais': 'vegetais', 'Tubérculos': 'tubérculos', 'Óleos': 'óleos',
        'Açúcares': 'açúcares', 'Bebidas': 'bebidas',
        'Ovos': 'ovos', 'Pães': 'pães', 'Nozes': 'nozes'
    }
    
    if 'arroz' in food_lower:
        return UNIT_CONVERSIONS_DATABASE['arroz']
    
    db_key = category_map.get(category, 'default')
    return UNIT_CONVERSIONS_DATABASE.get(db_key, UNIT_CONVERSIONS_DATABASE['default'])

# ===================================================================
# RUN THE SCRIPT
# ===================================================================

if __name__ == "__main__":
    process_multiple_datasets()