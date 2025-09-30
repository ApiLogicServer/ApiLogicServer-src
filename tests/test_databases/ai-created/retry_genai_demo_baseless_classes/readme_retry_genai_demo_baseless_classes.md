Issue 101: ChatGPT Failure - missing (Base) - not handled.

Copy tests/genai_tests/retry_bad_chatgpt/chatgpt_retry.response -> mgr:system/genai/temp/chatgpt_retry.response

The classes are missing (Base).

This cannot be easily repaired, since they are also missing _tablename_.

It is supposed to be caught and handled in the retry-3-times processing, 
but generates a bad project.  

Perhaps the related failure in test data generation caused that.  Under investigation.