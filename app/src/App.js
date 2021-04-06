import React, { useState, useEffect } from 'react';
import logo from './logo.svg';
import './App.css';
import ProgressBar from 'react-bootstrap/ProgressBar';
import 'bootstrap/dist/css/bootstrap.css';

import Header from './components/Header/Header';
import RegistrationForm from './components/RegistrationForm/RegistrationForm';
import LoginForm from './components/LoginForm/LoginForm';
import Home from './components/Home/Home';
import AlertComponent from './components/AlertComponent/AlertComponent';
import PrivateRoute from './utils/PrivateRoute';
import {
    BrowserRouter as Router,
    Switch,
    Route
  } from "react-router-dom";



function App() {
    const [title, updateTitle] = useState(null);
    const [errorMessage, updateErrorMessage] = useState(null);
    return (
      <Router>
      <div className="App">
        <Header title={title}/>
          <div className="container d-flex align-items-center flex-column">
            <Switch>
              <Route path="/" exact={true}>
                <RegistrationForm showError={updateErrorMessage} updateTitle={updateTitle}/>
              </Route>
              <Route path="/register">
                <RegistrationForm showError={updateErrorMessage} updateTitle={updateTitle}/>
              </Route>
              <Route path="/login">
                <LoginForm showError={updateErrorMessage} updateTitle={updateTitle}/>
              </Route>
              <PrivateRoute path="/home">
                <Home/>
              </PrivateRoute>
            </Switch>
            <AlertComponent errorMessage={errorMessage} hideError={updateErrorMessage}/>
          </div>
      </div>
      </Router>
    );
}

export default App;
