#
# Update List of Solana Tokens
#
curl https://raw.githubusercontent.com/solana-labs/token-list/main/src/tokens/solana.tokenlist.json \
  | jq \
  | grep "\"symbol\": " \
  | sort \
  > solana_tokens.txt \
  && sed -i "" "s|^      \"symbol\": ||" ./solana_tokens.txt
