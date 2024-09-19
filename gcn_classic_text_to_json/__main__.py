from gcn_classic_text_to_json.notices.alexis import conversion as alexis_conversion
from gcn_classic_text_to_json.notices.alexis import conversion as alexis_conversion
from gcn_classic_text_to_json.notices.calet import conversion as calet_conversion
from gcn_classic_text_to_json.notices.gecam import conversion as gecam_conversion
from gcn_classic_text_to_json.notices.sk_sn import conversion as sk_sn_conversion
from gcn_classic_text_to_json.notices.snews import conversion as snews_conversion

if __name__ == "__main__":
    alexis_conversion.create_all_alexis_jsons()
    calet_conversion.create_all_calet_jsons()
    gecam_conversion.create_all_gecam_jsons()
    sk_sn_conversion.create_all_sk_sn_jsons()
    snews_conversion.create_all_snews_jsons()
