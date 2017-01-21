import React from "react";
import {Table} from "react-bootstrap";

class Equipment extends React.Component {

  constructor(props) {
    super(props);
  }

  render() {
    return (
      <Table responsive hover={true} striped={true}>
        <thead>
        <tr>
          <th>Element</th>
          <th>Piece of equipment</th>
        </tr>
        </thead>
        <tbody>
        <tr>
          <td>Head</td>
          <td>an ushanka hat</td>
        </tr>
        <tr>
          <td>Body</td>
          <td>a shirt</td>
        </tr>
        <tr>
          <td>Legs</td>
          <td>a pair of trousers</td>
        </tr>
        <tr>
          <td>Left hand</td>
          <td>a sword</td>
        </tr>
        <tr>
          <td>Right hand</td>
          <td>a hammer</td>
        </tr>
        </tbody>
      </Table>);
  }
}

export default Equipment;
