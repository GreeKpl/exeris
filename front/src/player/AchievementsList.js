import React from "react";
import {ListGroup, ListGroupItem, Panel} from "react-bootstrap";

const AchievementEntry = ({title, children}) => (
  <ListGroupItem header={title}>
    {children}
  </ListGroupItem>
);

class AchievementsList extends React.Component {

  constructor(props) {
    super(props);
  }

  componentDidMount() {
    this.props.onMount();
  }

  render() {
    return <Panel header="Achievements">
      <ListGroup>
        {this.props.achievements.map(achievement =>
          <AchievementEntry key={achievement.get("title")}
                            title={achievement.get("title")}>
            {achievement.get("content")}
          </AchievementEntry>
        )}
      </ListGroup>
    </Panel>;
  }
}

export default AchievementsList;
