if [ ! -f "dict/epsd.npz" ]; then
  echo "Creaditng dictionary directory dict/"
  if [ ! -d "dict" ]; then
    mkdir dict
  fi
  cd dict
  echo "Scraping ePSD"
  ./scrape_epsd.sh
  echo "Extracting dictionary from ePSD"
  python extract_lexicon.py
  cd ..
fi

echo "Labeling commodities"
# commodify calls segment.py
# and convert/*
python commodify.py
