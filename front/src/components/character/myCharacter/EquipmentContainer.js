import {connect} from "react-redux";
import * as Immutable from "immutable";
import {getMyCharacterInfoFromMyCharacterState} from "../../../modules/myCharacter";
import React from "react";
import {Table, Panel} from "react-bootstrap";


const EquipmentPart = ({piece, name}) => {
  return <tr>
    <td>{piece}</td>
    <td>{name}</td>
  </tr>;
};

const EquipmentList = ({equipment}) => {
  return <Table fill responsive hover={true} striped={true}>
    <thead>
    <tr>
      <th>Element</th>
      <th>Piece of equipment</th>
    </tr>
    </thead>
    <tbody>
    {equipment.map((eqName, eqPart) =>
      <EquipmentPart
        piece={eqPart}
        name={eqName}
      />
    ).valueSeq()}
    </tbody>
  </Table>;
};

const NoEquipmentInfo = () => {
  return <p>
    Your character has no equipment
  </p>;
};

export const Equipment = ({equipment}) =>
  <Panel header="Equipment">
    {equipment.size > 0
      ? <EquipmentList equipment={equipment}/>
      : <NoEquipmentInfo/>}
  </Panel>;


const mapStateToProps = (state, ownProps) => {
  const myCharacterInfo = getMyCharacterInfoFromMyCharacterState(state, ownProps.characterId);
  return {
    characterId: ownProps.characterId,
    equipment: myCharacterInfo.get("equipment", Immutable.Map()),
  };
};

const mapDispatchToProps = (dispatch) => {
  return {}
};

const EquipmentContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(Equipment);

export default EquipmentContainer;
