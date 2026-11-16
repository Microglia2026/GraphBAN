# Input
# wkdir="/root/Software/GraphBAN/case_study/test"
# val_name="test_dataset_100.csv"
wkdir=$1
val_name=$2
# Core Code
val_data="${wkdir}/${val_name}"
run_model_py="/root/Software/GraphBAN/case_study/run_model.py"
predict_py="/root/Software/GraphBAN/case_study/predict.py"
# BindingBD
BindingBD_train_data="/root/Software/GraphBAN/case_study/bindingdb_train_data/source_train_bindingdb12.csv"
BindingBD_teacher_data="/root/Software/GraphBAN/case_study/bindingdb_train_data/bindingdb12_inductive_teacher_emb.parquet"
BindingBD_teacher_dir="${wkdir}/BindingBD"
BindingBD_result="${val_data%.csv}_BindingBD_pred.csv"
python $run_model_py --train_path $BindingBD_train_data --val_path $val_data --test_path $val_data --seed 12 --mode inductive --teacher_path $BindingBD_teacher_data --result_path $BindingBD_teacher_dir
python $predict_py --test_path $val_data --folder_path $BindingBD_teacher_dir --save_dir $BindingBD_result
# BioSNAP
BioSNAP_train_data="/root/Software/GraphBAN/case_study/biosnap_train_data/source_train_biosnap12.csv"
BioSNAP_teacher_data="/root/Software/GraphBAN/case_study/biosnap_train_data/biosnap12_inductive_teacher_emb.parquet"
BioSNAP_teacher_dir="${wkdir}/BioSNAP"
BioSNAP_result="${val_data%.csv}_BioSNAP_pred.csv"
python $run_model_py --train_path $BioSNAP_train_data --val_path $val_data --test_path $val_data --seed 12 --mode inductive --teacher_path $BioSNAP_teacher_data --result_path $BioSNAP_teacher_dir
python $predict_py --test_path $val_data --folder_path $BioSNAP_teacher_dir --save_dir $BioSNAP_result
# KIBA
KIBA_train_data="/root/Software/GraphBAN/case_study/kiba_train_data/source_train_kiba12.csv"
KIBA_teacher_data="/root/Software/GraphBAN/case_study/kiba_train_data/kiba12_inductive_teacher_emb.parquet"
KIBA_teacher_dir="${wkdir}/KIBA"
KIBA_result="${val_data%.csv}_KIBA_pred.csv"
python $run_model_py --train_path $KIBA_train_data --val_path $val_data --test_path $val_data --seed 12 --mode inductive --teacher_path $KIBA_teacher_data --result_path $KIBA_teacher_dir
python $predict_py --test_path $val_data --folder_path $KIBA_teacher_dir --save_dir $KIBA_result
