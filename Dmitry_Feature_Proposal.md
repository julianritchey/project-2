# Feature

***Notifier***

# What is the feature and what does it entail? 


This feature is relatively straightforward. After doing the market analyses in real time, as soon as the price reaches a certain level based on the indicator, the app will send a message to the user to buy/sell the stock, instead of buying the stock directly from the platform.


# Who does this feature target? 

Investors, who do not trust the bots to access their accounts and place the orders.

# Where in the application should the feature be implemented?

There will be a separate navigation tab for "Trading". Inside that tab there will be a checkbox for the users to receive the email from trades. 

# How will the feature be implemented?

Note, the analyses will need to be done preemptively in real time, which will include the following: API to read data in real time and Stock price analyses based on a certain indicator.

**if checkbox is true, then:**

@app.route('/send-email')
def send_email():
    recipient = 'recipient@example.com'
    subject = 'Sample Email'
    body = 'This is a sample email sent from Flask.'
    sender = app.config['MAIL_USERNAME']
    
    msg = Message(subject, sender=sender, recipients=[recipient])
    msg.body = body
    
    mail.send(msg)
    return 'Email sent successfully!'
