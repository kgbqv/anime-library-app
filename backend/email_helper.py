def registration_email(user_name):
    body = "Thank you for registering with us."
    html = f"""
    <html>
      <head>
        <style>
          @import url('https://fonts.googleapis.com/css2?family=Source+Code+Pro:ital,wght@0,200..900;1,200..900&display=swap');
          body {{
            margin: 0;
            display: flex;
            flex-direction: column;
            min-height: 100vh;
            font-family: 'Source Code Pro', monospace;
            background-color: #FAF3F0;
            padding: 20px;
          }}
          .container {{
            background-color: #FFF8F0;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
          }}
          h2 {{
            color: #FF8BA7;
          }}
          p {{
            font-size: 16px;
            color: #555;
          }}
          .footer {{
            margin-top: 20px;
            font-size: 0.8em;
            color: #888;
          }}
          .character-img {{
            width: 80px;
            height: 80px;
            border-radius: 50%;
            margin-bottom: 20px;
            border: 2px solid #FF8BA7;
          }}
        </style>
      </head>
      <body>
        <div class="container">
          <img src="https://animelibrarytestkhgb.netlify.app/.netlify/images?url=/assets/character2.png" alt="Character" class="character-img">
          <h2>Welcome, {user_name}!</h2>
          <p>Thank you for registering with our Library. Enjoy your reading journey!</p>
          <div class="footer">— The Library Team</div>
        </div>
      </body>
    </html>
    """
    return {
        "subject": "Welcome to the Pastel Library!",
        "html": html,
        "body": body
    }

def borrow_email(user_name, book_title, due_date):
    body = "Thank you for borrowing a book. Please return it in time."
    html = f"""
    <html>
      <head>
        <style>
          @import url('https://fonts.googleapis.com/css2?family=Source+Code+Pro:ital,wght@0,200..900;1,200..900&display=swap');
          body {{
            margin: 0;
            display: flex;
            flex-direction: column;
            min-height: 100vh;
            font-family: 'Source Code Pro', monospace;
            background-color: #F6F2F0;
            padding: 20px;
          }}
          .container {{
            background-color: #FFFFFF;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
          }}
          h2 {{
            color: #A7C7E7;
          }}
          p {{
            font-size: 16px;
            color: #555;
          }}
          .footer {{
            margin-top: 20px;
            font-size: 0.8em;
            color: #888;
          }}
          .character-img {{
            width: 80px;
            height: 80px;
            border-radius: 50%;
            margin-bottom: 20px;
            border: 2px solid #A7C7E7;
          }}
        </style>
      </head>
      <body>
        <div class="container">
          <img src="https://animelibrarytestkhgb.netlify.app/.netlify/images?url=/assets/character2.png" alt="Character" class="character-img">
          <h2>Hello, {user_name}!</h2>
          <p>You have borrowed <strong>{book_title}</strong>.</p>
          <p>Please return it by {due_date}.</p>
          <div class="footer">— The Library Team</div>
        </div>
      </body>
    </html>
    """
    return {
        "subject": "Your Book Borrowing Confirmation",
        "html": html,
        "body": body
    }

def return_email(user_name, book_title):
    body = "Thank you for return the book."
    html = f"""
    <html>
      <head>
        <style>
          @import url('https://fonts.googleapis.com/css2?family=Source+Code+Pro:ital,wght@0,200..900;1,200..900&display=swap');
          body {{
            margin: 0;
            display: flex;
            flex-direction: column;
            min-height: 100vh;
            font-family: 'Source Code Pro', monospace;
            background-color: #F8F4F0;
            padding: 20px;
          }}
          .container {{
            background-color: #FFFFFF;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
          }}
          h2 {{
            color: #C1E1C1;
          }}
          p {{
            font-size: 16px;
            color: #555;
          }}
          .footer {{
            margin-top: 20px;
            font-size: 0.8em;
            color: #888;
          }}
          .character-img {{
            width: 80px;
            height: 80px;
            border-radius: 50%;
            margin-bottom: 20px;
            border: 2px solid #C1E1C1;
          }}
        </style>
      </head>
      <body>
        <div class="container">
          <img src="https://animelibrarytestkhgb.netlify.app/.netlify/images?url=/assets/character2.png" alt="Character" class="character-img">
          <h2>Thank You, {user_name}!</h2>
          <p>You have successfully returned <strong>{book_title}</strong>.</p>
          <p>Your commitment to the library is appreciated.</p>
          <div class="footer">— The Library Team</div>
        </div>
      </body>
    </html>
    """
    return {
        "subject": "Book Return Confirmation",
        "html": html,
        "body": body
    }
