**Instructions to Set-up the Project:**

1.  Install python 3.7+

2.  Install pip

3.  Install virtualenv python library

   ```
   $ pip install virtualenv
   ```

4. Open Project Directory 

5. Create virtual environment

   ```
   $ virtualenv env
   ```

6.  Activate virtual Environment

   1. For Windows:

      ```
      $ ./env/Scripts/activate
      ```

7.  Install Dependencies

   ```
   $ pip install -r requirements.txt
   ```

8.  Run the flask Application

   ```
   $ ./app.py
   ```

9.  Open the website in browser [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

10. Before deploying the Project make sure to set *debug=False* in app.py