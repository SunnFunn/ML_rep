import pika, json, torch
from app.model import classifier, vectorizer

classifier.load_state_dict(torch.load('./app/model/model.pth'))
classifier.to('cpu')

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='rpc_queue')

def predict(body):
	vectorized_text = torch.tensor(vectorizer.vectorize(body, vector_length=100))
	
	result = classifier(vectorized_text.unsqueeze(0), apply_softmax=True)
	probability_values, indices = result.max(dim=1)
	predicted_category = vectorizer.category_vocab.lookup_index(indices.item())
	
	return predicted_category

	
def on_request(ch, method, props, body):
	print('got request: ', body.decode('UTF-8'))
	result = predict(body.decode('UTF-8'))
	ch.basic_publish(exchange='',routing_key=props.reply_to,
	                 properties=pika.BasicProperties(correlation_id = props.correlation_id),
	                 body=json.dumps(result))
	ch.basic_ack(delivery_tag=method.delivery_tag)
	
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='rpc_queue', on_message_callback=on_request)

print(" [x] Awaiting RPC requests")
channel.start_consuming()
