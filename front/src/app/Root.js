import React from "react";
import TopBarContainer from "../player/TopBarContainer";

const Root = (props) => {
  return <div>
    <TopBarContainer/>
    <br/><br/>
    {props.children}
  </div>
};

export default Root;
