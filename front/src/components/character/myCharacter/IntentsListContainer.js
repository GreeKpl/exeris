import {connect} from "react-redux";
import {getMyCharacterInfoFromMyCharacterState} from "../../../modules/myCharacter";
import * as Immutable from "immutable";
import React from "react";
import {Table, Panel, Button} from "react-bootstrap";


const IntentInfo = ({name, cancellable}) => {
  return <tr>
    <td>{name}</td>
    <td><Button disabled={!cancellable}>X</Button></td>
  </tr>;
};

export class IntentsList extends React.Component {

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

const mapStateToProps = (state, ownProps) => {

  const myCharacterInfo = getMyCharacterInfoFromMyCharacterState(state, ownProps.characterId);
  return {
    characterId: ownProps.characterId,
    intents: myCharacterInfo.get("allIntents", Immutable.List()),
  };
};

const mapDispatchToProps = (dispatch) => {
  return {}
};

const IntentsListContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(IntentsList);

export default IntentsListContainer;
