import csv
import json
import re

# ===================================================================
# CONFIGURATION SECTION - Modify these according to your needs
# ===================================================================

# Input and output file paths
INPUT_FILE = 'input_food_data.csv'
OUTPUT_FILE = 'output_food_data.csv'

# Default values for new columns that don't exist in source data
DEFAULT_CATEGORY = 'Alimentos'  # Default food category
DEFAULT_SOURCE = '#1food-moz.pdf'  # Source document reference
DEFAULT_PAGE = '1'  # Page number in source document

# ===================================================================
# COMPREHENSIVE UNIT CONVERSIONS DATABASE
# ===================================================================

# Standard unit conversions for different food categories
# Each food type has different density/volume relationships
UNIT_CONVERSIONS_DATABASE = {
    # CEREAIS E GRÃOS (Cereals and Grains)
    'cereais': {
        'defaultUnit': '100g',
        'units': ["100g", "gramas", "g", "xícara", "xícara de chá", "colher de sopa", "colher de chá", "kg"],
        'conversions': {
            "100g": 100,
            "gramas": 1,
            "g": 1,
            "xícara": 200,
            "xícara de chá": 200,
            "colher de sopa": 15,
            "colher de chá": 5,
            "kg": 1000
        }
    },
    
    # ARROZ (Rice varieties)
    'arroz': {
        'defaultUnit': '100g',
        'units': ["100g", "gramas", "g", "xícara", "xícara de chá", "colher de sopa", "colher de chá", "prato fundo", "prato raso", "concha", "kg"],
        'conversions': {
            "100g": 100,
            "gramas": 1,
            "g": 1,
            "xícara": 200,
            "xícara de chá": 200,
            "colher de sopa": 15,
            "colher de chá": 5,
            "prato fundo": 300,
            "prato raso": 150,
            "concha": 120,
            "kg": 1000
        }
    },
    
    # LEGUMINOSAS (Legumes - beans, lentils, etc)
    'leguminosas': {
        'defaultUnit': '100g',
        'units': ["100g", "gramas", "g", "xícara", "colher de sopa", "concha", "prato fundo", "kg"],
        'conversions': {
            "100g": 100,
            "gramas": 1,
            "g": 1,
            "xícara": 180,
            "colher de sopa": 12,
            "concha": 100,
            "prato fundo": 250,
            "kg": 1000
        }
    },
    
    # CARNES E AVES (Meats and Poultry)
    'carnes': {
        'defaultUnit': '100g',
        'units': ["100g", "gramas", "g", "bife", "filé", "peito", "coxa", "sobrecoxa", "fatia", "porção", "kg"],
        'conversions': {
            "100g": 100,
            "gramas": 1,
            "g": 1,
            "bife": 120,
            "filé": 150,
            "peito": 200,
            "coxa": 150,
            "sobrecoxa": 180,
            "fatia": 30,
            "porção": 150,
            "kg": 1000
        }
    },
    
    # PEIXES E FRUTOS DO MAR (Fish and Seafood)
    'peixes': {
        'defaultUnit': '100g',
        'units': ["100g", "gramas", "g", "filé", "posta", "unidade", "porção", "kg"],
        'conversions': {
            "100g": 100,
            "gramas": 1,
            "g": 1,
            "filé": 150,
            "posta": 200,
            "unidade": 180,
            "porção": 150,
            "kg": 1000
        }
    },
    
    # LATICÍNIOS (Dairy Products)
    'laticínios': {
        'defaultUnit': '100g',
        'units': ["100g", "gramas", "g", "ml", "litro", "copo", "xícara", "colher de sopa", "colher de chá", "fatia"],
        'conversions': {
            "100g": 100,
            "gramas": 1,
            "g": 1,
            "ml": 1.03,  # milk density
            "litro": 1030,
            "copo": 240,
            "xícara": 240,
            "colher de sopa": 15,
            "colher de chá": 5,
            "fatia": 20  # for cheese
        }
    },
    
    # FRUTAS (Fruits)
    'frutas': {
        'defaultUnit': '100g',
        'units': ["100g", "gramas", "g", "unidade", "unidade pequena", "unidade média", "unidade grande", "fatia", "rodela", "xícara", "colher de sopa", "kg"],
        'conversions': {
            "100g": 100,
            "gramas": 1,
            "g": 1,
            "unidade": 150,
            "unidade pequena": 100,
            "unidade média": 150,
            "unidade grande": 200,
            "fatia": 50,
            "rodela": 30,
            "xícara": 120,
            "colher de sopa": 15,
            "kg": 1000
        }
    },
    
    # VEGETAIS E HORTALIÇAS (Vegetables)
    'vegetais': {
        'defaultUnit': '100g',
        'units': ["100g", "gramas", "g", "unidade", "xícara", "colher de sopa", "colher de chá", "prato fundo", "prato raso", "folha", "kg"],
        'conversions': {
            "100g": 100,
            "gramas": 1,
            "g": 1,
            "unidade": 120,
            "xícara": 100,
            "colher de sopa": 10,
            "colher de chá": 3,
            "prato fundo": 200,
            "prato raso": 100,
            "folha": 10,
            "kg": 1000
        }
    },
    
    # TUBÉRCULOS (Tubers - potatoes, cassava, etc)
    'tubérculos': {
        'defaultUnit': '100g',
        'units': ["100g", "gramas", "g", "unidade", "unidade pequena", "unidade média", "unidade grande", "fatia", "pedaço", "xícara", "kg"],
        'conversions': {
            "100g": 100,
            "gramas": 1,
            "g": 1,
            "unidade": 180,
            "unidade pequena": 120,
            "unidade média": 180,
            "unidade grande": 250,
            "fatia": 40,
            "pedaço": 50,
            "xícara": 150,
            "kg": 1000
        }
    },
    
    # ÓLEOS E GORDURAS (Oils and Fats)
    'óleos': {
        'defaultUnit': '100g',
        'units': ["100g", "gramas", "g", "ml", "litro", "colher de sopa", "colher de chá", "fio"],
        'conversions': {
            "100g": 100,
            "gramas": 1,
            "g": 1,
            "ml": 0.92,  # oil density (lighter than water)
            "litro": 920,
            "colher de sopa": 13,
            "colher de chá": 4,
            "fio": 2
        }
    },
    
    # AÇÚCARES E DOCES (Sugars and Sweets)
    'açúcares': {
        'defaultUnit': '100g',
        'units': ["100g", "gramas", "g", "colher de sopa", "colher de chá", "xícara", "kg"],
        'conversions': {
            "100g": 100,
            "gramas": 1,
            "g": 1,
            "colher de sopa": 12,
            "colher de chá": 4,
            "xícara": 180,
            "kg": 1000
        }
    },
    
    # BEBIDAS (Beverages)
    'bebidas': {
        'defaultUnit': '100ml',
        'units': ["100ml", "ml", "litro", "copo", "xícara", "colher de sopa", "colher de chá"],
        'conversions': {
            "100ml": 100,
            "ml": 1,
            "litro": 1000,
            "copo": 240,
            "xícara": 240,
            "colher de sopa": 15,
            "colher de chá": 5
        }
    },
    
    # OVOS (Eggs)
    'ovos': {
        'defaultUnit': '100g',
        'units': ["100g", "gramas", "g", "unidade", "unidade pequena", "unidade média", "unidade grande", "clara", "gema"],
        'conversions': {
            "100g": 100,
            "gramas": 1,
            "g": 1,
            "unidade": 50,
            "unidade pequena": 40,
            "unidade média": 50,
            "unidade grande": 60,
            "clara": 30,
            "gema": 20
        }
    },
    
    # PÃES E MASSAS (Breads and Pasta)
    'pães': {
        'defaultUnit': '100g',
        'units': ["100g", "gramas", "g", "unidade", "fatia", "fatia fina", "fatia grossa", "pão francês", "pãozinho", "xícara", "kg"],
        'conversions': {
            "100g": 100,
            "gramas": 1,
            "g": 1,
            "unidade": 50,
            "fatia": 25,
            "fatia fina": 20,
            "fatia grossa": 35,
            "pão francês": 50,
            "pãozinho": 50,
            "xícara": 100,
            "kg": 1000
        }
    },
    
    # NOZES E SEMENTES (Nuts and Seeds)
    'nozes': {
        'defaultUnit': '100g',
        'units': ["100g", "gramas", "g", "unidade", "xícara", "colher de sopa", "colher de chá", "punhado", "kg"],
        'conversions': {
            "100g": 100,
            "gramas": 1,
            "g": 1,
            "unidade": 5,
            "xícara": 140,
            "colher de sopa": 10,
            "colher de chá": 3,
            "punhado": 30,
            "kg": 1000
        }
    },
    
    # DEFAULT (fallback for unclassified foods)
    'default': {
        'defaultUnit': '100g',
        'units': ["100g", "gramas", "g", "unidade", "porção", "colher de sopa", "colher de chá", "xícara", "kg"],
        'conversions': {
            "100g": 100,
            "gramas": 1,
            "g": 1,
            "unidade": 100,
            "porção": 150,
            "colher de sopa": 15,
            "colher de chá": 5,
            "xícara": 150,
            "kg": 1000
        }
    }
}

# ===================================================================
# MAIN CONVERSION FUNCTION
# ===================================================================

def convert_food_data(input_file, output_file):
    """
    Convert food data from original format to new structured format
    
    Args:
        input_file: Path to input CSV file
        output_file: Path to output CSV file
    """
    
    # Step 1: Open and read the input CSV file
    with open(input_file, 'r', encoding='utf-8') as infile:
        # Create a CSV reader object that reads the file as a dictionary
        # This allows us to access columns by their header names
        reader = csv.DictReader(infile)
        
        # Step 2: Prepare the output data structure
        output_rows = []
        
        # Track IDs to ensure uniqueness
        used_ids = set()
        
        # Step 3: Process each row from the input file
        for index, row in enumerate(reader, start=1):
            
            # Extract and clean the food description (remove quotes and trim)
            food_name = row['description'].strip().strip('"')
            
            # Generate unique ID from food name in snake_case
            food_id = generate_unique_id(food_name, used_ids)
            
            # Extract portion size (using 100g as default per your structure)
            portion_g = 100
            
            # Extract ALL nutritional values from source data
            # Convert to float if valid, otherwise use None (NULL in CSV)
            energy_kcal = safe_float(row.get('energy_kcal'))
            energy_kj = safe_float(row.get('energy_kj'))
            protein_g = safe_float(row.get('protein_g'))
            fat_g = safe_float(row.get('lipids_g'))  # Note: lipids = fats
            cholesterol_mg = safe_float(row.get('cholesterol_mg'))
            carbs_g = safe_float(row.get('carbohydrate_g'))
            fiber_g = safe_float(row.get('fiber_g'))
            ash_g = safe_float(row.get('ash_g'))
            
            # Minerals
            calcium_mg = safe_float(row.get('calcium_mg'))
            magnesium_mg = safe_float(row.get('magnesium_mg'))
            manganese_mg = safe_float(row.get('manganese_mg'))
            phosphorus_mg = safe_float(row.get('phosphorus_mg'))
            iron_mg = safe_float(row.get('iron_mg'))
            sodium_mg = safe_float(row.get('sodium_mg'))
            potassium_mg = safe_float(row.get('potassium_mg'))
            copper_mg = safe_float(row.get('copper_mg'))
            zinc_mg = safe_float(row.get('zinc_mg'))
            
            # Vitamins
            retinol_mcg = safe_float(row.get('retinol_mcg'))
            re_mcg = safe_float(row.get('re_mcg'))
            rae_mcg = safe_float(row.get('rae_mcg'))
            thiamine_mg = safe_float(row.get('thiamine_mg'))
            riboflavin_mg = safe_float(row.get('riboflavin_mg'))
            pyridoxine_mg = safe_float(row.get('pyridoxine_mg'))
            niacin_mg = safe_float(row.get('niacin_mg'))
            vitamin_c_mg = safe_float(row.get('vitamin_c_mg'))
            
            # Moisture
            moisture_pct = safe_float(row.get('moisture_pct'))
            
            # Step 4: Create COMPREHENSIVE nutritionPer100g JSON structure
            # This includes ALL nutritional values from the source data
            nutrition_per_100g = {
                # Main macronutrients
                "calories": energy_kcal,
                "energy_kj": energy_kj,
                "protein": protein_g,
                "fat": fat_g,
                "carbs": carbs_g,
                "fiber": fiber_g,
                "cholesterol": cholesterol_mg,
                "moisture": moisture_pct,
                "ash": ash_g,
                
                # Minerals
                "calcium": calcium_mg,
                "magnesium": magnesium_mg,
                "manganese": manganese_mg,
                "phosphorus": phosphorus_mg,
                "iron": iron_mg,
                "sodium": sodium_mg,
                "potassium": potassium_mg,
                "copper": copper_mg,
                "zinc": zinc_mg,
                
                # Vitamins
                "retinol": retinol_mcg,
                "re": re_mcg,
                "rae": rae_mcg,
                "thiamine": thiamine_mg,
                "riboflavin": riboflavin_mg,
                "pyridoxine": pyridoxine_mg,
                "niacin": niacin_mg,
                "vitamin_c": vitamin_c_mg
            }
            
            # Remove None values from the nutrition dictionary for cleaner JSON
            nutrition_per_100g = {k: v for k, v in nutrition_per_100g.items() if v is not None}
            
            # Convert to JSON string
            nutrition_json = json.dumps(nutrition_per_100g, ensure_ascii=False)
            
            # Step 5: Determine category and get appropriate unit conversions
            category = categorize_food(food_name)
            unit_config = get_unit_config(food_name, category)
            
            # Step 6: Create the output row with all required fields
            output_row = {
                'id': food_id,
                'name': food_name,
                'portion_g': portion_g,
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
                'nutritionPer100g': nutrition_json,
                'category': category,
                'source_pdf': DEFAULT_SOURCE,
                'page': DEFAULT_PAGE,
                'notes': f'Entry {index} from source table'
            }
            
            # Add the processed row to output list
            output_rows.append(output_row)
        
        # Step 7: Write all processed data to output CSV file
        if output_rows:
            # Define the column order for output file
            fieldnames = [
                'id', 'name', 'portion_g', 'energy_kcal', 'protein_g', 
                'fat_g', 'carbs_g', 'fiber_g', 'calcium_mg', 'iron_mg', 
                'sodium_mg', 'defaultUnit', 'units', 'unitConversions', 
                'nutritionPer100g', 'category', 'source_pdf', 'page', 'notes'
            ]
            
            # Open output file and write data
            with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                
                # Write header row
                writer.writeheader()
                
                # Write all data rows
                writer.writerows(output_rows)
            
            print(f"✓ Conversion completed successfully!")
            print(f"✓ Processed {len(output_rows)} food items")
            print(f"✓ Output saved to: {output_file}")
            print(f"\n📊 Nutritional data included per 100g:")
            print(f"   - Macronutrients: calories, protein, fat, carbs, fiber")
            print(f"   - Minerals: calcium, iron, sodium, potassium, magnesium, etc.")
            print(f"   - Vitamins: A, B complex, C")
            print(f"   - Other: cholesterol, moisture, ash")
        else:
            print("✗ No data found in input file")

# ===================================================================
# HELPER FUNCTIONS
# ===================================================================

def generate_unique_id(food_name, used_ids):
    """
    Generate a unique snake_case ID from food name
    Handles duplicates by appending numbers
    
    Args:
        food_name: Original food name
        used_ids: Set of already used IDs
    Returns:
        Unique snake_case ID string
    """
    # Step 1: Convert to lowercase
    name_lower = food_name.lower()
    
    # Step 2: Remove special characters and replace spaces/commas with underscores
    # Keep only letters, numbers, and underscores
    name_clean = re.sub(r'[^\w\s]', '', name_lower)  # Remove special chars
    name_clean = re.sub(r'\s+', '_', name_clean)     # Replace spaces with _
    name_clean = re.sub(r'_+', '_', name_clean)      # Replace multiple _ with single _
    name_clean = name_clean.strip('_')                # Remove leading/trailing _
    
    # Step 3: Ensure ID is not empty
    if not name_clean:
        name_clean = 'food_item'
    
    # Step 4: Handle duplicates by appending numbers
    base_id = name_clean
    counter = 1
    final_id = base_id
    
    while final_id in used_ids:
        final_id = f"{base_id}_{counter}"
        counter += 1
    
    # Add to used IDs set
    used_ids.add(final_id)
    
    return final_id

def safe_float(value):
    """
    Safely convert a value to float, handling NA, Tr (trace), and empty values
    
    Args:
        value: String value from CSV
    Returns:
        Float value or None if invalid
    """
    if not value or value.upper() in ['NA', 'TR', '']:
        return None
    try:
        return float(value)
    except ValueError:
        return None

def format_value(value):
    """
    Format a value for CSV output (None becomes NULL string)
    
    Args:
        value: Numeric value or None
    Returns:
        Formatted string
    """
    return 'NULL' if value is None else str(value)

def categorize_food(food_name):
    """
    Categorize food based on keywords in the name
    Returns both display category and internal category key
    
    Args:
        food_name: Name of the food item
    Returns:
        Category string for display
    """
    food_lower = food_name.lower()
    
    # Define category keywords with Portuguese terms
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
    
    # Check each category for keyword matches
    for category, keywords in categories.items():
        if any(keyword in food_lower for keyword in keywords):
            return category
    
    # Return default category if no match found
    return DEFAULT_CATEGORY

def get_unit_config(food_name, category):
    """
    Get the appropriate unit configuration based on food name and category
    
    Args:
        food_name: Name of the food item
        category: Category of the food
    Returns:
        Dictionary with defaultUnit, units list, and conversions
    """
    food_lower = food_name.lower()
    
    # Map display categories to internal database keys
    category_map = {
        'Cereais': 'cereais',
        'Leguminosas': 'leguminosas',
        'Carnes': 'carnes',
        'Peixes': 'peixes',
        'Laticínios': 'laticínios',
        'Frutas': 'frutas',
        'Vegetais': 'vegetais',
        'Tubérculos': 'tubérculos',
        'Óleos': 'óleos',
        'Açúcares': 'açúcares',
        'Bebidas': 'bebidas',
        'Ovos': 'ovos',
        'Pães': 'pães',
        'Nozes': 'nozes'
    }
    
    # Check for specific food type first (more specific than category)
    if 'arroz' in food_lower:
        return UNIT_CONVERSIONS_DATABASE['arroz']
    
    # Then check category mapping
    db_key = category_map.get(category, 'default')
    return UNIT_CONVERSIONS_DATABASE.get(db_key, UNIT_CONVERSIONS_DATABASE['default'])

# ===================================================================
# RUN THE SCRIPT
# ===================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Food Data Conversion Script - COMPREHENSIVE VERSION")
    print("=" * 60)
    print(f"Input file: {INPUT_FILE}")
    print(f"Output file: {OUTPUT_FILE}")
    print("=" * 60)
    
    try:
        convert_food_data(INPUT_FILE, OUTPUT_FILE)
    except FileNotFoundError:
        print(f"✗ Error: Could not find input file '{INPUT_FILE}'")
        print("  Please make sure the file exists in the same directory")
    except Exception as e:
        print(f"✗ Error during conversion: {str(e)}")
        print("  Please check your input file format")