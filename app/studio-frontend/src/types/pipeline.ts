export type PipelineStageMeta = {
  id: string;
  name: string;
  order?: number;
  description: string;
};

export type PipelineAgentMeta = {
  id: string;
  name: string;
  stages: string[];
  cursor_agent: string;
  skill: { id: string; name: string };
};

export type PipelineSkillMeta = {
  id: string;
  name: string;
};

export type PipelineMetadataResponse = {
  stages: PipelineStageMeta[];
  agents: PipelineAgentMeta[];
  skills: PipelineSkillMeta[];
  summary: {
    stage_count: number;
    agent_count: number;
    skill_count: number;
    transition_count: number;
  };
  source_refs: string[];
};
