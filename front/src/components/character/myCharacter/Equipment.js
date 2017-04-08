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

const Equipment = ({equipment}) =>
  <Panel header="Equipment">
    {equipment.size > 0
      ? <EquipmentList equipment={equipment}/>
      : <NoEquipmentInfo/>}
  </Panel>;

export default Equipment;
