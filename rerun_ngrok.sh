if pgrep -x "ngrok" > /dev/null; then
    echo "ngrok is already running. Exiting..."
    exit 1
fi


ngrok http 80 --log=stdout | while read -r line; do
    if [[ $line == *"msg=\"started tunnel\""* ]]; then
        ngrok_url=$(echo "$line" | grep -oE 'https://[a-zA-Z0-9.-]+')
        slack_webhook_url="https://hooks.slack.com/services/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"
        curl -X POST -H 'Content-type: application/json' --data "{\"text\":\"New ngrok URL: $ngrok_url\"}" "$slack_webhook_url"
        echo "Captured ngrok URL: $ngrok_url"
        break
    fi
done

# slack_webhook_url="https://hooks.slack.com/services/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"
# curl -X POST -H 'Content-type: application/json' --data "{\"text\":\"New ngrok URL: $ngrok_url\"}" "$slack_webhook_url"





