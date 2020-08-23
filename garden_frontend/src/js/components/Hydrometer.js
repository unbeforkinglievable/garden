import React from 'react';
import ReactDOM from 'react-dom';

class Hydrometer extends React.Component {
    constructor() {
        super();
    };

    onClick(event) {
        // debug
        console.log('Clicked; sending http request');

        // send http request to server
        // FIXME: this is not working
        const Http = new XMLHttpRequest();
        const url = 'http://127.0.0.1:5000/sense';
        Http.open('GET', url);
        Http.send();

        // display the response
        Http.onreadystatechange=(e)=>{
            console.log('http reponse: ' + Http.responseText);
        };
    };

    render() {
        return React.createElement(
            'button',
            {
                id:"poll-hydrometer-btn",
                type:"button",
                class:"btn btn-success",
                onClick: () => this.onClick()
            },
            'Poll Hydrometer'
        );
    };
}

export default Hydrometer;

const wrapper = document.getElementById("root");
wrapper ? ReactDOM.render(React.createElement(Hydrometer), wrapper) : false;
