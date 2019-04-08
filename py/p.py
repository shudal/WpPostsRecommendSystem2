from sklearn.feature_extraction.text import TfidfVectorizer

tf = TfidfVectorizer(analyzer='word', ngram_range=(1, 3), min_df=0, stop_words='english')

import os
import configparser
import pymysql
print("Reading config...")
cur_path=os.path.dirname(os.path.realpath(__file__))
config_path=os.path.join(cur_path,'config.ini')
conf=configparser.ConfigParser()
conf.read(config_path)

#从配置文件中获取数据信息
db_host             = conf.get('database', 'host')
db_port             = int(conf.get('database', 'port'))
db_user             = conf.get('database', 'user')
db_password         = conf.get('database', 'password')
db_database_name    = conf.get('database','database')
db_table_prefix     = conf.get('database', 'table_prefix')
db_config = {'host' : db_host, 'port' : db_port, 'user' : db_user, 'password' : db_password, 'db' : db_database_name, 'prefix' : db_table_prefix}

print("Connecting database...")
#连接数据库
db = pymysql.connect(host = db_config['host'],port = db_config['port'], user = db_config['user'], password  = db_config['password'], db = db_config['db'], charset = 'utf8mb4')
cursor = db.cursor()


import datetime
today = datetime.date.today()
preweek = today - datetime.timedelta(days=8)
sql_query_posts = "select ID,post_content from " + db_config['prefix'] + "_posts p where p.post_date > '" + str(preweek)  + "' and post_status='publish' and post_type='post'"
cursor.execute(sql_query_posts)
posts = cursor.fetchall()

post_ids = []
id2index = {}
post_contents = []
for i in range(0, len(posts)):
	id2index[str(posts[i][0])] = i
	post_ids.append(posts[i][0])
	post_contents.append(posts[i][1])

print("The number of posts:" + str(len(post_contents)))

tfidf_matrix = tf.fit_transform(post_contents)
print(id2index)

from sklearn.metrics.pairwise import linear_kernel
cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

def get_recommendations(postid, cosine_sim = cosine_sim):
	idx = id2index[str(postid)]
	sim_scores = list(enumerate(cosine_sim[idx]))
	sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
	sim_scores = sim_scores[1:11]	
	post_indices = [i[0] for i in sim_scores]
	return post_indices

