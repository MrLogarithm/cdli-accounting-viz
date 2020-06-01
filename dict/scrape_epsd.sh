IFS='
'

if [ ! -d epsd ]; then
  mkdir epsd
  mkdir epsd/forms
fi

url_base="http://psd.museum.upenn.edu/epsd/cf-toc-"
url_forms="http://psd.museum.upenn.edu/cgi-bin/xff?xff="
for letter in {A,B,D,E,G,NG,H,I,K,L,M,N,P,R,S,SH,T,U,W,Y,Z}; do
  echo Scraping letter $letter...
  if [ -f epsd/cf-toc-$letter.html ]; then
    rm epsd/cf-toc-$letter.html
  fi
  wget -P epsd/ ${url_base}${letter}.html
  for line in $( cat epsd/cf-toc-${letter}.html |grep "showarticle\|popxff" ); do
    # Some sed distros don't support extended regex, so for
    # compatibility reasons we don't use (showarticle|popxff)
    if echo $line | grep -q "popxff"; then
      echo pop
      num=$( echo $line |sed "s/^.*popxff('\([^']*\)').*$/\1/g" )
    else
      num=$( echo $line |sed "s/^.*showarticle('\([^']*\).html').*$/\1/g" )
    fi
    echo Fetch details for $num:
    wget -P epsd/forms ${url_forms}${num} -O epsd/forms/$num
  done
done
