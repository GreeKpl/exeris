import React from "react";
import {Table, ProgressBar, Panel} from "react-bootstrap";
import {i18nize} from "../../../i18n";


const Skill = ({name, value, indent = false}) => {
  return <tr>
    <td style={indent ? {paddingLeft: "30px"} : {}}>{name}</td>
    <td><ProgressBar now={value * 100} label={(value * 100) + "%"} striped/></td>
  </tr>;
};

class SkillsList extends React.Component {

  constructor(props) {
    super(props);
  }

  render() {
    const {t} = this.props;

    return (
      <Panel header={t("panel_skills")}>
        <Table responsive fill>
          <thead>
          <tr>
            <th>{t("skills_header_name")}</th>
            <th>{t("skills_header_level")}</th>
          </tr>
          </thead>
          <tbody>
          {this.props.mainSkills.map(generalSkill =>
            [
              <Skill
                name={generalSkill.get("name")}
                value={generalSkill.get("value")}
                key={generalSkill.get("name")}
              />
            ].concat(
              generalSkill.get("children").map(specificSkill => {
                return <Skill
                  indent={true}
                  name={specificSkill.get("name")}
                  value={specificSkill.get("value")}
                  key={specificSkill.get("name")}
                />;
              })
            )
          )}
          </tbody>
        </Table>
      </Panel>
    );
  }
}

export default i18nize(SkillsList);
