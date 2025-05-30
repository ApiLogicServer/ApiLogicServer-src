# Updates local genai-logic project (at org_git)
# update 4/27/2025 - should no longer be required with WebGenAI install simplification

# Before running, run BLT
# This will copy:
#    1. manager samples to the local genai-logic project
#    2. webgenai from prototypes/manager to the local genai-logic project

# cd samples
# sh run.sh nw_sample_nocust

echo "\n\nRun Samples using webgenai docker coontainer"

if [ $# -eq 0 ]
  then
    echo " "
    # echo "shell: $SHELL"
    echo " eg:"
    echo " "
    echo "   > cd ApiLogicServer-src"
    echo "   > sh docker/webgenie_docker/build_genai_logic.sh [go]"
    echo " "
    exit 0
fi

echo "\nblt:"
blt='../../build_and_test/ApiLogicServer'
ls $blt


echo "\nsrc:"
src='api_logic_server_cli/prototypes/manager'
ls $src

echo "\ngenai_logic:"
genailogic='../genai_logic'
ls $genailogic

echo " "

cp -r $blt/samples/nw_sample $genailogic/samples
cp -r $blt/samples/nw_sample_nocust $genailogic/samples
# (omit tutorial - and research this next one...)
cp -r $src/webgenai $genailogic
cp $src/run_sample.sh $genailogic
cp $src/run_webgenai.sh $genailogic

echo "\nCompleted.\n\n "