<html>
<head>
</head>
<body>
%if created:
Your account has been suggessfully created! You may now log in.
%else:
<h2>Simple Registration Form</h2>
% if errors:
	% for e in errors:
	<ul>
	  <li><b>${e}</b></li>
	</ul>
	% endfor
% endif
<form method="POST" action="/registration/simple">
<table>
<tr>
<td>Username</td><td><input name="username" type="text" /></td>
</tr>
<tr>
<td>Password</td><td><input name="password" type="password" /></td>
</tr>
<tr>
<td>Password Confirm</td><td><input name="password-confirm" type="password" /></td>
</tr>
<tr>
<td>Email</td><td><input name="email" type="text" /></td>
</tr>
<tr>
<td><input name="submit" type="submit" value="Register" /></td>
</tr>
</table>
</form>
%endif
</body>
</html>
