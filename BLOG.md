# Why naive RAG fails in enterprise vs. how Aegis solves it

While learning and building in the AI engineering we need to go through with the major peak and that is RAG and when i read about this, learnt about this and built about this then i understood why the RAG is the one of the most important thing in the whole AI engineering becuase its solves a very crucial problem for the AI and that is keeping AI grounded with the actual source and the documents of your with keeping the rules with these so i also tried to build a one use case that is the enterprise rag assitant : 

A company with departments: HR, finance, engineering, support. Each owns its own documents. Leave policy
and compensation belong to HR, reimbursement and discount approvals to finance, error codes and the
security policy to engineering, refunds and shipping and warranty to support.
An employee should be able to ask a question in plain language instead of hunting through a shared drive. And
the part that makes this a secure assistant:

NOT EVERYONE MAY READ EVERYTHING
Someone in HR must not be able to pull engineering's restricted documents, and a guest from outside
the company must see almost nothing. In most RAG demos this is skipped. Here it is the centre of the
design, which is why access control is applied in SQL before the search runs rather than filtered out
afterwards.

