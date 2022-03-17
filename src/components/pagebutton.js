import React from 'react';
import Button from '@mui/material/Button';
import ButtonGroup from '@mui/material/ButtonGroup';
import { react } from '@babel/types';


export default function PageButton(props){

    if (!props.show){
        return null
    }


    return(
        <ButtonGroup variant="contained" aria-label="outlined primary button group">
            <Button disabled= {props.disableback} onClick = {() => {
                if(props.pagenum !== 1){
                    props.sexyProp(props.pagenum-1);
                    props.searchCallback();
                }
            }}> {"<"} </Button>
            <Button>Page {props.pagenum +""}</Button>
            <Button onClick={() => {
                props.sexyProp(props.pagenum + 1);
                props.searchCallback();
            }}> {">"} </Button>
        </ButtonGroup>
    )
}