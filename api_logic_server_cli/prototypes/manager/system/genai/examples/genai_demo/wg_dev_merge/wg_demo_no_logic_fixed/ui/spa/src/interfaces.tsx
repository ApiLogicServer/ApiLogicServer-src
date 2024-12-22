export interface ISection {
    subtitle: string;
    label: string;
    Type: any;
    images: any;
    id: string;
    title: string;
    name: string;
    content: string;
    order: number;
    paragraph: string;
    template: string;
    background: string;
    style: any;
}
  
export interface IPageData {
    id: string;
    name: string;
    SectionList?: ISection[];
}

