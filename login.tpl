%#template for a user to provide a username
<form action="/" method="get">
  Username:
  <input type="text" name="username" value="" size="20" maxlength="20">
  %if err:
    <inline style="color:red">{{err}}</inline>
  %end
  <br>
  <input type="submit" name="login" value="login">
</form>