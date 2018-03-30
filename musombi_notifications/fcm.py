import os, string, random, firebase_admin, hashlib, datetime
from django.conf import settings
from firebase_admin import db, messaging, credentials
from colour import Color

class FCM:
    

    def __init__(self):        
        
        dir_path = os.path.dirname(os.path.realpath(__file__)) 

        ## TODO use a more secure config for this (up to you)       
        cred = credentials.Certificate(dir_path+'/cred.json')

        try: 
            print("Firebase {0} initialised".format(firebase_admin.get_app().name))

        except ValueError:
            print("Initialising Firebase")
            firebase_admin.initialize_app(cred, {
                'databaseURL' : 'https://push-b573a.firebaseio.com'
            })
            print("Firebase {0} initialised".format(firebase_admin.get_app().name))    

    def __chunks__(self,l, n):
        for i in range(0, len(l), n):
            yield l[i:i + n]
    
    def __is_list_of_strings__(self,lst):
        if lst and isinstance(lst, list):
            return all(isinstance(elem, str) for elem in lst)
        else:
            return False

    def __check_color__(self,color):        
        try:
            # Converting 'deep sky blue' to 'deepskyblue'
            color = color.replace(" ", "")
            Color(color)
            # if everything goes fine then return True
            return True
        except ValueError: # The color code was not found
            return False

    def __get_token__(self,user_ids):    
        if not isinstance(user_ids, str):
            raise TypeError("user_id must be a string when sending a single message")  
               
        token = db.reference('tokens/{0}'.format(user_ids)).get()
        return token

    def __get_token_list__(self,user_ids):
            
        if not self.__is_list_of_strings__(user_ids):
            raise TypeError("user_id must be a list when sending bulk message")
    
        tokens = list(map(lambda x:self.__get_token__(x),user_ids))
        return tokens

    def __handle_register_response__(self,register_response):
        ## TO-DO Handle errors when not all devices are registered (For Christian)
        ## Checkout https://firebase.google.com/docs/cloud-messaging/admin/manage-topic-subscriptions#subscribe_to_a_topic
        ## Success Count
        print(register_response.success_count, "tokens were subscribed successfully")

        ## Fail count
        print(register_response.failure_count, "tokens were not subscribed successfully")

        ## Error (Handle this error, don't just print it)
        print(register_response.errors, "Maybe empty, maybe not") 

    def __create_or_get_topic__(self,user_ids):
        
        if not self.__is_list_of_strings__(user_ids):
            raise TypeError("user_id must be a list when sending bulk message")
    
        topic = ",".join(user_ids).encode('utf-8')
        topic_sha = hashlib.sha1(topic).hexdigest()       
        topic_ref = db.reference('topics/{0}'.format(topic_sha))
        topic_result = topic_ref.get()

        if topic_result is None:
            tokens = self.__get_token_list__(user_ids)            
            register_response = messaging.subscribe_to_topic(tokens, topic_sha)
            self.__handle_register_response__(register_response)             
            topic_ref.set(topic_sha)
            topic_result = topic_sha

        return topic_result
        
    def __get_all_tokens__(self):
        
        tokenMap = db.reference('tokens').get()
        tokens = list(map(lambda x:tokenMap[x],tokenMap))
        return tokens    


    def __get_chunk_topic__(self,chunk):

        # print(chunk)
        topic = ",".join(chunk).encode('utf-8')
        topic_sha = hashlib.sha1(topic).hexdigest()       
        topic_ref = db.reference('all_user_topics_test/{0}'.format(topic_sha))
        topic_result = topic_ref.get()

        if topic_result is None:
           
            register_response = messaging.subscribe_to_topic(chunk, topic_sha)
            self.__handle_register_response__(register_response)   
            topic_ref.set(topic_sha)
            topic_result = topic_sha

        return topic_result        


    def __create__topics_for__all__users__(self):

        tokens = self.__get_all_tokens__()
        chunks = list(self.__chunks__(tokens,2))
        topics = []
        for i, chunk in enumerate(chunks):
            topics.append(self.__get_chunk_topic__(chunk))
            print(i)

        return topics

        
    def __send__(self,user_id,notification,data,dry_run=False):
        
        if not isinstance(user_id, str):
            raise TypeError("user_id must be a string when send a single message")  
        
        if not isinstance(notification, messaging.AndroidNotification):
            raise TypeError("notification must be of the type AndroidNotification")  
        
        if not isinstance(data, dict):
            raise TypeError("custom data must be of the type Dictionary")

        registration_token = self.__get_token__(user_id)


        message = messaging.Message(
            data=data,
            android=messaging.AndroidConfig(
                ttl=datetime.timedelta(seconds=3600),
                priority='normal',
                notification=notification,
            ),
            token=registration_token
        )

        return messaging.send(message,dry_run=dry_run)
         
    def __send_to_topic__(self,topic,message,dry_run=False):
        
        if not isinstance(message, messaging.Message):
            raise TypeError("message must be of the type Message") 

        if not isinstance(topic, str):
            raise TypeError("topic must be of the type String")              
                
        return messaging.send(message,dry_run=dry_run)



    def __send_many__(self,user_ids,notification,data,dry_run=False):
        
        if not self.__is_list_of_strings__(user_ids):
            raise TypeError("user_id must be a list when sending bulk message")
        
        if not isinstance(notification, messaging.AndroidNotification):
            raise TypeError("notification must be of the type AndroidNotification")  
        
        if not isinstance(data, dict):
            raise TypeError("custom data must be of the type Dictionary")
    
        topic = self.__create_or_get_topic__(user_ids)
        

        message = messaging.Message(
            data=data,
            android=messaging.AndroidConfig(
                ttl=datetime.timedelta(seconds=3600),
                priority='normal',
                notification=notification,
            ),
            topic=topic
        )

        
        return messaging.send(message,dry_run=dry_run)

        

    def __send_all__(self,notification,data,dry_run=False):
       
        if not isinstance(notification, messaging.AndroidNotification):
            raise TypeError("notification must be of the type AndroidNotification")  
        
        if not isinstance(data, dict):
            raise TypeError("custom data must be of the type Dictionary")
    
        topics = self.__create__topics_for__all__users__()

        responses = []

        for i, topic in enumerate(topics):
            print(i)
            responses = messaging.send(
                            messaging.Message(
                                data=data,
                                android=messaging.AndroidConfig(
                                    ttl=datetime.timedelta(seconds=3600),
                                    priority='normal',
                                    notification=notification,
                                ),
                                topic=topic
                            ),
                            dry_run=dry_run
                        )

        return responses        
    
    ## Send to one or many users, can either take a list of user_ids or a single user_id
    def sendNotification(self,user_ids,title,body=None,data=None,color=None,dry_run=False):
        """Sends notifications to a user or group or users

        Args:
          user_ids: A string or list of strings of users to receive the notification (Mandatory)
          title: A title for the notification (Mandatory), is of type string
          body: A body for the notification (Optional), is of type string
          color: A color for the notification (Optional), is of type string -- red is default
          data: A dictionary for the custom data attribute in the notification 
          dry_run: A boolean indicating whether to run the operation in dry run mode (optional).

        Returns:
          response: A message ID string that uniquely identifies the sent the message.

        Raises:
          ValueError: If user_ids or title is None or Color is invalid
          ApiCallError: If an error occurs while communicating with the remote database server.
          TypeError: If types are incorrect
        """

        if user_ids is None:
            raise ValueError("user_ids must be supplied as a string or list of strings")
        
        if title is None:
            raise ValueError("title must be supplied as a string")
        
        if color is None:
            color = '#f45342'
        if body is None:
            body = '\n'
        if data is None:
            data = {
                'message': 'None'
            }

        # user_ids_type_valid = (not isinstance(user_ids, str)) and (not self.__is_list_of_strings__(user_ids))  )
       
        if not isinstance(user_ids, str) and not self.__is_list_of_strings__(user_ids):
            raise TypeError("user_id must be a string or list of strings")
        if not isinstance(title, str):
            raise TypeError("title must be a string")
        if not isinstance(body, str):
            raise TypeError("body must be a string")
        if not isinstance(color, str):
            raise TypeError("color must be a sring")
        if not self.__check_color__(color):
            raise ValueError("Invalid Color")        
        
        notification=messaging.AndroidNotification(
            title=title,
            body=body,
            color=color
        )      

        if isinstance(user_ids, str):    
            response = self.__send__(user_ids,notification,data,dry_run=dry_run)
        elif self.__is_list_of_strings__(user_ids):
            response = self.__send_many__(user_ids,notification,data,dry_run=dry_run)
        else:
            raise Exception("Unknown error occured")

        return response

    def sendNotificationToAll(self,title,body=None,data=None,color=None,dry_run=False):
        """Sends Notifications to all users           

        Args:
          title: A title for the notification (Mandatory), is of type string
          body: A body for the notification (Optional), is of type string
          color: A color for the notification (Optional), is of type string -- red is default
          data: A dictionary for the custom data attribute in the notification 
          dry_run: A boolean indicating whether to run the operation in dry run mode (optional).

        Returns:
          responses: A list of  message ID strings that uniquely identifies the sent the notification.

        Raises:
          ValueError: If user_ids or title is None or Color is invalid
          ApiCallError: If an error occurs while communicating with the remote database server.
          TypeError: If types are incorrect
        """

        if title is None:
            raise ValueError("title must be supplied as a string")
        
        if color is None:
            color = '#f45342'
        if body is None:
            body = '\n'
        if data is None:
            data = {
                'message': 'None'
            }
       
        if not isinstance(title, str):
            raise TypeError("title must be a string")
        if not isinstance(body, str):
            raise TypeError("body must be a string")
        if not isinstance(color, str):
            raise TypeError("color must be a sring")
        if not self.__check_color__(color):
            raise Exception("Invalid Color")        
        
        notification=messaging.AndroidNotification(
            title=title,
            body=body,
            color=color
        )      

        responses = self.__send_all__(notification,data,dry_run=dry_run)

        return responses



    



    

        




