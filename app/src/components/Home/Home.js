import { withRouter } from 'react-router-dom';
import { ACCESS_TOKEN_NAME, API_BASE_URL } from '../../constants/apiConstants';
import axios from 'axios'

import React, { useState, useEffect } from 'react';
import ProgressBar from 'react-bootstrap/ProgressBar';
import 'bootstrap/dist/css/bootstrap.css';
import './Home.css';


function Home(props) {
    // useEffect(() => {
    //     //axios.get(API_BASE_URL+'/user/me', { headers: { 'token': localStorage.getItem(ACCESS_TOKEN_NAME) }})
    //     axios.get(API_BASE_URL+'/user/me', { headers: {"Authorization": "Basic " + btoa(localStorage.getItem(ACCESS_TOKEN_NAME) + ":unused")}})
    //     .then(function (response) {
    //         if(response.status !== 200){
    //           redirectToLogin()
    //         }
    //     })
    //     .catch(function (error) {
    //       redirectToLogin()
    //     });
    //   })
    // function redirectToLogin() {
    // props.history.push('/login');
    // }





    const [average, setAverage] = useState(0);
    const [median, setMedian] = useState(0);
    const [count, setCount] = useState(0);
    const [id, setId] = useState(0);
    const [progress, setProgress] = useState('0');
    const [url, setUrl] = useState('');
    const [ignoreList, setIgnoreList] = useState('');

    // this changes time variable every second
    const [time, setTime] = useState(Date.now());
    useEffect(() => {
        const interval = setInterval(function() {
                setTime(Date.now());
        }, 1000);
        return () => {
            clearInterval(interval);
        };

        }, []
    );


    const onInputChange = (event) => {
        setUrl(event.target.value);
    }
    const onIgnoreListChange = (event) => {
        setIgnoreList(event.target.value);
    }


    // Only get id for this search request
    function onSubmit(event) {
        event.preventDefault();
        const requestOptions = {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Basic ' + btoa(localStorage.getItem(ACCESS_TOKEN_NAME) + ':unused')
            },
            body: JSON.stringify({ url: url, ignore_list: ignoreList })
        };
        fetch('/api/olx_get_id/', requestOptions).then(res => res.json()).then(data => {
            setId(data.id);
            checkResult(data.id);
        })
    }
    // Fetch result for specific id
    function checkResult(id) {
        const requestOptions = {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Basic ' + btoa(localStorage.getItem(ACCESS_TOKEN_NAME) + ':unused')
            },
            body: JSON.stringify({ id: id })
        };
        setProgress('1');
        setAverage('...');
        setMedian('...');
        setCount('...');
        fetch('/api/olxresult/', requestOptions).then(res => res.json()).then(data => {
            setAverage(data.average);
            setMedian(data.median);
            setCount(data.count);
        })
    }

    // Check progress for specific id
    useEffect(() => {
        const requestOptions = {
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Basic ' + btoa(localStorage.getItem(ACCESS_TOKEN_NAME) + ':unused')
            }
        };
        if (progress !== '0' && progress !== '100') {
            fetch('/api/progress/'+id, requestOptions).then(res => res.json()).then(data => {
                setProgress(data.progress);
            });
        }
        
    }, [time]);


    return (
        <div className="App">
            <header className="App-header">
                <h1>OLX-link price scrapper</h1></header>
                <form onSubmit={onSubmit}>
                    
                    <p>Enter custom OLX search link with some filters.</p>
                    <label htmlFor="url">URL:</label>
                    <div><textarea id="url" size="40" rows="4" cols="70" type="text" onChange={onInputChange} /></div>
                    <label htmlFor="ignoreList">Ignore words in titles (space-separated):</label>
                    <div><textarea id="ignoreList" size="40" rows="1" cols="70" type="text" onChange={onIgnoreListChange} /></div>
                    <input className="btn btn-outline-primary" type="submit" value="OK" />
                </form>
                <p>Scraping progress: {progress} %</p>

                <div className="container w-50" >{progressBar(progress)}</div>
                <div className="container w-50 p-3" >
                <ul className="list-group text-left">
                <li className="list-group-item list-group-item-primary" >Average price is {average} zl</li>
                <li className="list-group-item list-group-item-primary">Median is {median} zl</li>
                <li className="list-group-item list-group-item-primary">Item count is {count}</li>
                </ul>
                </div>
                <br />
            
        </div>
    );
}

function progressBar(progress) {
    if (progress === '100') {
        return (
            <ProgressBar now={progress} />
        );
    }
    return (
        <ProgressBar animated now={progress} label={`${progress}%`} />
    );
}

export default withRouter(Home);
