# Security audit

Because we focused most of our energy on getting the project up and running, we didn't spend a lot of time fixing security vulnerabilities. Thus, there are quite a lot, though some of them are automatically taken care of by Django.

(Note: We have the `DEBUG` setting set to `True` for the code on this repo so that users can run and debug the code on their own. However, for the purposes of this security audit, we assume that `DEBUG` is set to `False`. Otherwise, users would be able to obtain a wealth of information just by triggering an error somehow and looking at the debug data - and there are lots of ways to trigger errors by manually sending invalid requests through the URL.

Similarly, even though `dj_database_url` has `ssl_require=False`, assume that it has `ssl_require=True` for the purposes of this audit.)

Here are some vulnerabilities and our comments on whether they have been patched or not. Thankfully, most of them have already been patched by the framework (Python + Django). Also, this is by no means an exhaustive list, though we hope there are not too many more.

1. SQL injection: Django interfaces with the database through Querysets, which automatically escape the input, so we are fine.
2. Cross-site scripting (XSS): Django templates escape all variables by [default](https://code.djangoproject.com/wiki/AutoEscaping), so we are fine.
3. Cross-site request forgery (CSRF): Django automatically requires a CSRF token for any form processing, so we are fine.
4. Password exploitation: Passwords stored in the database are encrypted using the default hash function. This is better than storing them as plain text (which is so vulnerable that one of my sources described storing plaintext passwords as a sin), but it is still less than ideal. The encrypted passwords are not salted, meaning no random string is added to the password before it is encrypted. This makes it less secure since a hacker with a list of the hash results of some of the most common passwords could look for those hashes in a database. Salting the encryption would prevent this since any hacker would be forced to recalculate the hash values for all common passwords with the salt added, an extremely time consuming process. However, it is still possible to make this more secure. We could use a different hash function than the default. The [Django documentation](https://docs.djangoproject.com/en/2.2/topics/auth/passwords/) highlights two: Argon2, which is made to not be easier to compute on specialized hardware that a hacker might use, and bcrypt, which is designed for long term password storage. We could also increase the rounds of hashing, which means the function is performed more times, requiring more computing power to convert passwords to hash values. This means it will take slightly longer for the server to validate a password, but it will take a hacker much longer to guess and check the hash values of possible passwords.
5. Man-in-the-middle: Django ensures that connections are encrypted with SSL.
6. Privilege escalation: We don't have any admin roles besides the default Django admin feature, which should be secure.
7. Buffer overflow: The nature of Python itself avoids buffer overflow, according to [Wikipedia](https://en.wikipedia.org/wiki/Buffer_overflow#Choice_of_programming_language).
8. [Session fixation](https://en.wikipedia.org/wiki/Session_fixation): The Django `session` feature creates new `sessionid`'s at each login, so `sessionid`'s can't be forced.
9. Denial of service: We don't have any protection against DoS attacks, but it's doubtful that we'll need to for the scope of this project.
