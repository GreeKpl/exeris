import React from "react";
import {Table, ProgressBar} from "react-bootstrap";

class SkillsList extends React.Component {

  constructor(props) {
    super(props);
  }

  render() {
    return (
      <Table responsive>
        <thead>
        <tr>
          <th>Skill</th>
          <th>Level</th>
        </tr>
        </thead>
        <tbody>
        <tr>
          <td>Cooking</td>
          <td><ProgressBar now={50} label="50%" striped/></td>
        </tr>
        <tr>
          <td>Baking</td>
          <td><ProgressBar now={20} label="20%" striped/></td>
        </tr>
        <tr>
          <td>Confectionery</td>
          <td><ProgressBar now={80} label="80%" striped/></td>
        </tr>
        </tbody>
      </Table>
    );
  }
}

export default SkillsList;
