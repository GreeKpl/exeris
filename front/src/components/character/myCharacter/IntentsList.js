import React from "react";
import {Table, Panel, Button} from "react-bootstrap";


const IntentInfo = ({name, cancellable}) => {
  return <tr>
    <td>{name}</td>
    <td><Button disabled={!cancellable}>X</Button></td>
  </tr>;
};

class IntentsList extends React.Component {

  render() {
    return <Panel header="Intents">
      <Table responsive fill>
        <tbody>
        {this.props.intents.map(intentInfo =>
          <IntentInfo
            name={intentInfo.get("name")}
            cancellable={intentInfo.get("cancellable")}
            key={intentInfo.get("name")}
          />)}
        </tbody>
      </Table>
    </Panel>;
  }
}

export default IntentsList;
