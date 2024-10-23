from gcn_classic_text_to_json.notices.alexis import conversion as alexis_conversion
from gcn_classic_text_to_json.notices.calet import conversion as calet_conversion

if __name__ == "__main__":
    calet_conversion.create_all_calet_jsons()
    alexis_conversion.create_all_alexis_jsons()
