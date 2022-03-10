import logo from './logo.svg';
import './App.css';
import * as React from 'react';
import Button from '@mui/material/Button';
import ButtonGroup from '@mui/material/ButtonGroup';
import SearchButton from './components/serachbutton';
import SearchField from './components/search';
import { styled } from '@mui/material/styles';
import Typography from '@mui/material/Typography';
import Options from './components/options'
import JsonResults from './example.json'
import Box from '@mui/material/Box';
import research_logo from './logos/Re-Search-logos_transparent.png';


function App() {

  const [search, setSearch] = React.useState('');


  function Search() {
    return fetch('http://127.0.0.1:5000/' + search).then(response => response.json()).then(data => console.log(data));
  }

  function TextEntered(searchval) {
    setSearch(searchval);
  }


  return (
    <div className="App" style={{
      // width: '100%',
      marginLeft: '5em',
      marginRight: '5em'
    }}>
      <div className="logo">
        <img src={research_logo} className="center" width="25%" height="10%" />
      </div>
      <div className='SearchOptions' style={{
      }}>
        <SearchField
          style={{ maxWidth: '80%' }}
          parentCallback={TextEntered}
        />
        <div className='Options'>
          <Options />
        </div>
      </div>
      <SearchButton parentCallback={Search} />
      <div>
        {JsonResults.Results.map((name, key) => {
          return <Box bgcolor="#E8E8E8"
          //  display="flex" //probably dont need this anymore but keeping it here just in case...
          //  sx={{ overflow: 'auto' }}
          //  sx={{ width: '50%' }}
          //  style={{justifyContent: "center"}}
          //  style={{alignItems: "center"}}
          //  style={{position: "relative"}}
            marginTop={1}
            padding={2}
          >
            <p key={key}>
              <p><font COLOR="grey" SIZE="2" face="Arial">{name.url}</font></p>
              <a href={name.url}><font COLOR="green" SIZE="5" face="Arial">{name.title}</font></a>
              <p><font COLOR="grey" face="Arial">{name.date}</font></p>
              <p><font face="Arial">{name.description}</font></p>
              <p><font face="Arial">Author(s): {name.authors}</font></p>
            </p></Box>;
        })}
      </div>
    </div>
  )

}


export default App;