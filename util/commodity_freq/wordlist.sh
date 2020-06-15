# Produces a list of words which occur within two tokens of a numeral:
cat data/girsu/transliteration.txt |grep -v "^&" |grep -o ") \([^ ]* \)\{2\}" |tr " " "\n" |tr -d "#[]*?\!<>" |grep -v "^ *[0-9]/\?[0-9]*(" |grep -v "\(,\|(\|)\)" |grep -v "^$" |sort |uniq -c |sort -n
