import React, { useState } from 'react';
import Header from '../Header/Header';
import './Register.css';

const Register = () => {
  const [form, setForm] = useState({firstName: '', lastName: '', userName: '', email: '', password: '', confirm: ''});
  const [error, setError] = useState('');

  const submit = async (event) => {
    event.preventDefault();
    if (form.password !== form.confirm) return setError('Passwords do not match.');
    if (form.password.length < 8) return setError('Password must be at least 8 characters.');
    const response = await fetch('/djangoapp/register', {
      method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(form)
    });
    const result = await response.json();
    if (!response.ok) return setError(result.error || 'Registration failed.');
    sessionStorage.setItem('username', result.userName);
    sessionStorage.setItem('firstname', result.firstName || '');
    sessionStorage.setItem('lastname', result.lastName || '');
    window.location.href = '/dealers';
  };

  return <>
    <Header />
    <form className="register_container inputs" onSubmit={submit}>
      <h1 className="header">Sign Up</h1>
      {[
        ['firstName', 'First name'], ['lastName', 'Last name'],
        ['userName', 'Username'], ['email', 'Email'],
        ['password', 'Password'], ['confirm', 'Confirm password']
      ].map(([field, label]) => <label className="input" key={field}>
        {label}
        <input className="input_field" type={field.includes('password') || field === 'confirm' ? 'password' : field === 'email' ? 'email' : 'text'}
          required value={form[field]} onChange={(event) => setForm({...form, [field]: event.target.value})} />
      </label>)}
      {error && <p role="alert">{error}</p>}
      <button className="submit" type="submit">Create account</button>
      <p>Already registered? <a href="/login">Log in</a></p>
    </form>
  </>;
};

export default Register;
