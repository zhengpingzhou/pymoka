##################################################################################
# Personal machine learning experiment manager with ZSH tab completion.
# 
# Usage:
# $ moka <exp>                  #==> prints path to configuration file
# $ moka <exp> <operation>      #==> executes operation for experiment exp
# $ moka <exp1> -- <exp2>       #==> copies the configuration file from exp1 to exp2
# $ moka-tb <exp1> ... <expN>   #==> opens tensorboard for exp1~expN in same window
#                                    (max: 10 experiments)
##################################################################################


# --------------------------------------------------------------------------------
moka()
{
    python -m moka.launcher $@
    if [[ "$#" -eq "1" ]]; then
        EXP=$1
        echo "configs/$EXP.sh"
    elif [[ "$#" -eq "3" ]]; then
        EXP=$3
        echo "configs/$EXP.sh"
    fi
}

_moka() {
  local state

  _arguments \
    '1: :->exp1'\
    '3: :->exp3'\
    '*: :->others'

  FOLDER="$PWD/configs"
  FILEEXT=".sh"

  # Take the basename of files in $FOLDER and ends with $FILEEXT
  local files=()
  for f in $FOLDER/*$FILEEXT; do
      files+=("${${f/$FILEEXT/}/$FOLDER\/}");
  done

  case $state in
      (exp1) _arguments '1:profiles:( $files )' ;;
      (exp3) _arguments '3:profiles:( $files )' ;;
      (*) compadd "$@" ''
  esac
}

compdef _moka moka

# --------------------------------------------------------------------------------
function join_by { local IFS="$1"; shift; echo "$*"; }


moka-tb() {
    local args=()
    for EXP in $@; do
        args+=("${EXP}:exp/${EXP}/tb")
    done
    arg=$(join_by , "${args[@]}")
    tensorboard --logdir $arg 2>/dev/null
}


_moka_tb() {
  local state

  _arguments \
    '1: :->exp1'\
    '2: :->exp2'\
    '3: :->exp3'\
    '4: :->exp4'\
    '5: :->exp5'\
    '6: :->exp6'\
    '7: :->exp7'\
    '8: :->exp8'\
    '9: :->exp9'\
    '10: :->exp10'\
    '*: :->others'

  FOLDER="$PWD/exp"
  FILEEXT=""

  # Take the basename of files in $FOLDER and ends with $FILEEXT
  local files=()
  for f in $FOLDER/*$FILEEXT; do
      files+=("${${f/$FILEEXT/}/$FOLDER\/}");
  done

  case $state in
      (exp1) _arguments '1:profiles:( $files )' ;;
      (exp2) _arguments '2:profiles:( $files )' ;;
      (exp3) _arguments '3:profiles:( $files )' ;;
      (exp4) _arguments '4:profiles:( $files )' ;;
      (exp5) _arguments '5:profiles:( $files )' ;;
      (exp6) _arguments '6:profiles:( $files )' ;;
      (exp7) _arguments '7:profiles:( $files )' ;;
      (exp8) _arguments '8:profiles:( $files )' ;;
      (exp9) _arguments '9:profiles:( $files )' ;;
      (exp10) _arguments '10:profiles:( $files )' ;;
      (*) compadd "$@" ''
  esac
}

compdef _moka_tb moka-tb