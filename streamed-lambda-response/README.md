An example lambda that streams a response using flask


packaging the lambda
from inside streamed lambda response directory
  pip3 install --target ./package -r requirements.txt  && cd package && zip -r ../lambda.zip . && cd .. && zip lambda.zip app.py && zip lambda.zip run.sh && zip lambda.zip requirements.txt && mv lambda.zip .. && cd .. && terraform apply 