# Usage: bash pipline.sh <wkdir> <output_csv_name> <database_name> <uniprot_accession>
# Example: bash pipline.sh /root/WorkSpace/1.YH/3.NRF1 TCMBank_Q16656.csv TCMBank Q16656
if [ "$#" -ne 4 ]; then
    echo "Usage: bash pipline.sh <wkdir> <output_csv_name> <database_name> <uniprot_accession>" >&2
    exit 2
fi

# wkdir="$1"
# val_name="$2"
# database_name="$3"
# uniprot_accession="$4"

wkdir="/root/WorkSpace/1.YH/3.NRF1/GraphBAN"
val_name="TCMBank_Q16656.csv"
database_name="TCMBank"
uniprot_accession="Q16656"

# Core Code
val_data="${wkdir}/${val_name}"
database_data="/root/Software/GraphBAN/DataBase/${database_name}.csv"
prepare_protein_py="/root/Software/GraphBAN/prepare_protein_input.py"
predict_py="/root/Software/GraphBAN/inductive_mode/predict.py"
combine_predictions_py="/root/Software/GraphBAN/combine_predictions.py"

# 准备输入文件
python "$prepare_protein_py" --input "$database_data" --output "$val_data" --accession "$uniprot_accession"

# BindingBD
BindingBD_model="/root/Software/GraphBAN/inductive_mode/trained_models/bindingdb/inductive/seed12/result/best_model_epoch_13.pth"
BindingBD_result="${val_data%.csv}_BindingBD_pred.csv"
python "$predict_py" --test_path "$val_data" --trained_model "$BindingBD_model" --save_dir "$BindingBD_result"

# BioSNAP
BioSNAP_model="/root/Software/GraphBAN/inductive_mode/trained_models/biosnap/inductive/seed12/result/best_model_epoch_45.pth"
BioSNAP_result="${val_data%.csv}_BioSNAP_pred.csv"
python "$predict_py" --test_path "$val_data" --trained_model "$BioSNAP_model" --save_dir "$BioSNAP_result"

# KIBA
KIBA_model="/root/Software/GraphBAN/inductive_mode/trained_models/kiba/inductive/seed12/result/best_model_epoch_7.pth"
KIBA_result="${val_data%.csv}_KIBA_pred.csv"
python "$predict_py" --test_path "$val_data" --trained_model "$KIBA_model" --save_dir "$KIBA_result"

# 筛选
combined_result="${val_data%.csv}_GraphBAN_pred.csv"
unfiltered_result="${val_data%.csv}_BindingBD_BioSNAP_KIBA_pred.csv"
python "$combine_predictions_py"  --bindingbd "$BindingBD_result" --biosnap "$BioSNAP_result" \
    --kiba "$KIBA_result" --output "$combined_result" \
    --unfiltered-output "$unfiltered_result" --threshold 0.5

