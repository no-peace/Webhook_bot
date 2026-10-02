# Repository Context Group: pkg_magic-backup-importer_core
# Source Repository: discohook/discohook

### File: `packages/magic-backup-importer/README.md`
```md
# Magic Backup Importer

This app is placed on the `discohook.org` domain and allows users to transfer their local browser backups to the cloud (`discohook.app`).

## Development

- Clone the repository and navigate to this package
- Create a `.dev.vars` file and populate it:
  - `DISCOHOOK_ORIGIN` - the [origin](https://developer.mozilla.org/en-US/docs/Web/API/URL/origin) of your Discohook process
- Install dependencies with `yarn install`
- Run `yarn dev`

## Attribution

Files in the `app/database` directory were borrowed and modified from the original [discohook/site](https://github.com/discohook/site/tree/daf7be22e0887caa96a36f3bdd49fbaad877d3d8/modules/database) around March 15, 2024, licensed under AGPL-3.0.

```

### File: `packages/magic-backup-importer/app/components/Button.tsx`
```tsx
export enum ButtonStyle {
  Primary = 1,
  Secondary = 2,
}

export const Button = (
  props: React.DetailedHTMLProps<
    React.ButtonHTMLAttributes<HTMLButtonElement>,
    HTMLButtonElement
  > & { discordStyle?: ButtonStyle },
) => {
  const { discordStyle, ...rest } = props;
  let color = "bg-blurple-500 hover:bg-blurple-600 active:bg-blurple-700";
  if (discordStyle === ButtonStyle.Secondary) {
    color = "bg-[#4e5058] hover:bg-[#6d6f78]";
  }

  return (
    <button
      type="button"
      {...rest}
      className={`rounded font-medium text-base min-h-[36px] max-h-9 py-0 px-[14px] min-w-[60px] text-white transition disabled:opacity-40 disabled:cursor-not-allowed inline-flex ${color} ${
        rest.className ?? ""
      }`}
    />
  );
};

```

### File: `packages/magic-backup-importer/app/components/Checkbox.tsx`
```tsx
export const Checkbox = (
  props: React.DetailedHTMLProps<
    React.InputHTMLAttributes<HTMLInputElement>,
    HTMLInputElement
  > & {
    label: React.ReactNode;
    description?: React.ReactNode;
  },
) => {
  const { label, description } = props;

  return (
    <div>
      <label className="flex group/checkbox select-none">
        <input type="checkbox" {...props} className="hidden peer" />
        <ConditionalBox className={props.className} check />
        <ConditionalBox className={props.className} />
        <p className="text-sm font-medium flex">{label}</p>
      </label>
      {description && <div>{description}</div>}
    </div>
  );
};

const ConditionalBox: React.FC<{ check?: boolean; className?: string }> = ({
  check,
  className,
}) => (
  <div
    className={`rounded border h-5 w-5 bg-gray-300 border-gray-200 group-hover/checkbox:bg-gray-400 peer-focus:border-blurple-500 dark:border-gray-600 dark:group-hover/checkbox:bg-gray-600 dark:bg-gray-700 transition-all mr-1 ${
      check
        ? "hidden peer-checked:inline-flex"
        : "inline-flex peer-checked:hidden"
    } ${className ?? ""}`}
  >
    {check && <i className="ci-Check m-auto mr-[2px] transition" />}
  </div>
);

```

### File: `packages/magic-backup-importer/app/coolicons.css`
```css
@font-face {
  font-family: "coolicons";
  src:
    url("/fonts/coolicons.ttf?44fbbv") format("truetype"),
    url("/fonts/coolicons.woff?44fbbv") format("woff"),
    url("/fonts/coolicons.svg?44fbbv#coolicons") format("svg");
  font-weight: normal;
  font-style: normal;
  font-display: block;
}

i {
  /* use !important to prevent issues with browser extensions that change fonts */
  /* biome-ignore lint/a11y/useGenericFontNames: it's an icon font, there's no sensible fallback */
  font-family: "coolicons" !important;
  speak: never;
  font-style: normal;
  font-weight: normal;
  font-variant: normal;
  text-transform: none;
  line-height: 1;

  /* Better Font Rendering =========== */
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.ci-Add_Column:before {
  content: "\e900";
}
.ci-Add_Minus_Square:before {
  content: "\e901";
}
.ci-Add_Plus_Circle:before {
  content: "\e902";
}
.ci-Add_Plus_Square:before {
  content: "\e903";
}
.ci-Add_Plus:before {
  content: "\e904";
}
.ci-Add_Row:before {
  content: "\e905";
}
.ci-Add_To_Queue:before {
  content: "\e906";
}
.ci-Airplay:before {
  content: "\e907";
}
.ci-Alarm:before {
  content: "\e908";
}
.ci-Archive:before {
  content: "\e909";
}
.ci-Arrow_Circle_Down_Left:before {
  content: "\e90a";
}
.ci-Arrow_Circle_Down_Right:before {
  content: "\e90b";
}
.ci-Arrow_Circle_Down:before {
  content: "\e90c";
}
.ci-Arrow_Circle_Left:before {
  content: "\e90d";
}
.ci-Arrow_Circle_Right:before {
  content: "\e90e";
}
.ci-Arrow_Circle_Up_Left:before {
  content: "\e90f";
}
.ci-Arrow_Circle_Up_Right:before {
  content: "\e910";
}
.ci-Arrow_Circle_Up:before {
  content: "\e911";
}
.ci-Arrow_Down_Left_LG:before {
  content: "\e912";
}
.ci-Arrow_Down_Left_MD:before {
  content: "\e913";
}
.ci-Arrow_Down_Left_SM:before {
  content: "\e914";
}
.ci-Arrow_Down_LG:before {
  content: "\e915";
}
.ci-Arrow_Down_MD:before {
  content: "\e916";
}
.ci-Arrow_Down_Right_LG:before {
  content: "\e917";
}
.ci-Arrow_Down_Right_MD:before {
  content: "\e918";
}
.ci-Arrow_Down_Right_SM:before {
  content: "\e919";
}
.ci-Arrow_Down_SM:before {
  content: "\e91a";
}
.ci-Arrow_Down_Up:before {
  content: "\e91b";
}
.ci-Arrow_Left_LG:before {
  content: "\e91c";
}
.ci-Arrow_Left_MD:before {
  content: "\e91d";
}
.ci-Arrow_Left_Right:before {
  content: "\e91e";
}
.ci-Arrow_Left_SM:before {
  content: "\e91f";
}
.ci-Arrow_Reload_02:before {
  content: "\e920";
}
.ci-Arrow_Right_LG:before {
  content: "\e921";
}
.ci-Arrow_Right_MD:before {
  content: "\e922";
}
.ci-Arrow_Right_SM:before {
  content: "\e923";
}
.ci-Arrow_Sub_Down_Left:before {
  content: "\e924";
}
.ci-Arrow_Sub_Down_Right:before {
  content: "\e925";
}
.ci-Arrow_Sub_Left_Down:before {
  content: "\e926";
}
.ci-Arrow_Sub_Left_Up:before {
  content: "\e927";
}
.ci-Arrow_Sub_Right_Down:before {
  content: "\e928";
}
.ci-Arrow_Sub_Right_Up:before {
  content: "\e929";
}
.ci-Arrow_Sub_Up_Left:before {
  content: "\e92a";
}
.ci-Arrow_Sub_Up_Right:before {
  content: "\e92b";
}
.ci-Arrow_Undo_Down_Left:before {
  content: "\e92c";
}
.ci-Arrow_Undo_Down_Right:before {
  content: "\e92d";
}
.ci-Arrow_Undo_Up_Left:before {
  content: "\e92e";
}
.ci-Arrow_Undo_Up_Right:before {
  content: "\e92f";
}
.ci-Arrow_Up_Left_LG:before {
  content: "\e930";
}
.ci-Arrow_Up_Left_MD:before {
  content: "\e931";
}
.ci-Arrow_Up_Left_SM:before {
  content: "\e932";
}
.ci-Arrow_Up_LG:before {
  content: "\e933";
}
.ci-Arrow_Up_MD:before {
  content: "\e934";
}
.ci-Arrow_Up_Right_LG:before {
  content: "\e935";
}
.ci-Arrow_Up_Right_MD:before {
  content: "\e936";
}
.ci-Arrow_Up_Right_SM:before {
  content: "\e937";
}
.ci-Arrow_Up_SM:before {
  content: "\e938";
}
.ci-Arrows_Reload_01:before {
  content: "\e939";
}
.ci-Bar_Bottom:before {
  content: "\e93a";
}
.ci-Bar_Left:before {
  content: "\e93b";
}
.ci-Bar_Right:before {
  content: "\e93c";
}
.ci-Bar_Top:before {
  content: "\e93d";
}
.ci-Bell_Add:before {
  content: "\e93e";
}
.ci-Bell_Close:before {
  content: "\e93f";
}
.ci-Bell_Notification:before {
  content: "\e940";
}
.ci-Bell_Off:before {
  content: "\e941";
}
.ci-Bell_Remove:before {
  content: "\e942";
}
.ci-Bell_Ring:before {
  content: "\e943";
}
.ci-Bell:before {
  content: "\e944";
}
.ci-Bold:before {
  content: "\e945";
}
.ci-Book_Open:before {
  content: "\e946";
}
.ci-Book:before {
  content: "\e947";
}
.ci-Bookmark:before {
  content: "\e948";
}
.ci-Building_01:before {
  content: "\e949";
}
.ci-Building_02:before {
  content: "\e94a";
}
.ci-Building_03:before {
  content: "\e94b";
}
.ci-Building_04:before {
  content: "\e94c";
}
.ci-Bulb:before {
  content: "\e94d";
}
.ci-Calendar_Add:before {
  content: "\e94e";
}
.ci-Calendar_Check:before {
  content: "\e94f";
}
.ci-Calendar_Close:before {
  content: "\e950";
}
.ci-Calendar_Days:before {
  content: "\e951";
}
.ci-Calendar_Event:before {
  content: "\e952";
}
.ci-Calendar_Remove:before {
  content: "\e953";
}
.ci-Calendar_Week:before {
  content: "\e954";
}
.ci-Calendar:before {
  content: "\e955";
}
.ci-Camera:before {
  content: "\e956";
}
.ci-Car_Auto:before {
  content: "\e957";
}
.ci-Caret_Circle_Down:before {
  content: "\e958";
}
.ci-Caret_Circle_Left:before {
  content: "\e959";
}
.ci-Caret_Circle_Right:before {
  content: "\e95a";
}
.ci-Caret_Circle_Up:before {
  content: "\e95b";
}
.ci-Caret_Down_MD:before {
  content: "\e95c";
}
.ci-Caret_Down_SM:before {
  content: "\e95d";
}
.ci-Caret_Left_SM:before {
  content: "\e95e";
}
.ci-Caret_Right_SM:before {
  content: "\e95f";
}
.ci-Caret_Up_MD:before {
  content: "\e960";
}
.ci-Caret_Up_SM:before {
  content: "\e961";
}
.ci-Chart_Bar_Horizontal_01:before {
  content: "\e962";
}
.ci-Chart_Bar_Vertical_01:before {
  content: "\e963";
}
.ci-Chart_Line:before {
  content: "\e964";
}
.ci-Chart_Pie:before {
  content: "\e965";
}
.ci-Chat_Add:before {
  content: "\e966";
}
.ci-Chat_Check:before {
  content: "\e967";
}
.ci-Chat_Circle_Add:before {
  content: "\e968";
}
.ci-Chat_Circle_Check:before {
  content: "\e969";
}
.ci-Chat_Circle_Close:before {
  content: "\e96a";
}
.ci-Chat_Circle_Dots:before {
  content: "\e96b";
}
.ci-Chat_Circle_Remove:before {
  content: "\e96c";
}
.ci-Chat_Circle:before {
  content: "\e96d";
}
.ci-Chat_Close:before {
  content: "\e96e";
}
.ci-Chat_Conversation_Circle:before {
  content: "\e96f";
}
.ci-Chat_Conversation:before {
  content: "\e970";
}
.ci-Chat_Dots:before {
  content: "\e971";
}
.ci-Chat_Remove:before {
  content: "\e972";
}
.ci-Chat:before {
  content: "\e973";
}
.ci-Check_All_Big:before {
  content: "\e974";
}
.ci-Check_All:before {
  content: "\e975";
}
.ci-Check_Big:before {
  content: "\e976";
}
.ci-Check:before {
  content: "\e977";
}
.ci-Checkbox_Check:before {
  content: "\e978";
}
.ci-Checkbox_Fill:before {
  content: "\e979";
}
.ci-Checkbox_Unchecked:before {
  content: "\e97a";
}
.ci-Chevron_Down_Duo:before {
  content: "\e97b";
}
.ci-Chevron_Down:before {
  content: "\e97c";
}
.ci-Chevron_Left_Duo:before {
  content: "\e97d";
}
.ci-Chevron_Left_MD:before {
  content: "\e97e";
}
.ci-Chevron_Left:before {
  content: "\e97f";
}
.ci-Chevron_Right_Duo:before {
  content: "\e980";
}
.ci-Chevron_Right_MD:before {
  content: "\e981";
}
.ci-Chevron_Right:before {
  content: "\e982";
}
.ci-Chevron_Up_Duo:before {
  content: "\e983";
}
.ci-Chevron_Up:before {
  content: "\e984";
}
.ci-Chromecast:before {
  content: "\e985";
}
.ci-Circle_Check:before {
  content: "\e986";
}
.ci-Circle_Help:before {
  content: "\e987";
}
.ci-Circle_Warning:before {
  content: "\e988";
}
.ci-Circle:before {
  content: "\e989";
}
.ci-Clock:before {
  content: "\e98a";
}
.ci-Close_Circle:before {
  content: "\e98b";
}
.ci-Close_LG:before {
  content: "\e98c";
}
.ci-Close_MD:before {
  content: "\e98d";
}
.ci-Close_SM:before {
  content: "\e98e";
}
.ci-Close_Square:before {
  content: "\e98f";
}
.ci-Cloud_Add:before {
  content: "\e990";
}
.ci-Cloud_Check:before {
  content: "\e991";
}
.ci-Cloud_Close:before {
  content: "\e992";
}
.ci-Cloud_Download:before {
  content: "\e993";
}
.ci-Cloud_Off:before {
  content: "\e994";
}
.ci-Cloud_Remove:before {
  content: "\e995";
}
.ci-Cloud_Upload:before {
  content: "\e996";
}
.ci-Cloud:before {
  content: "\e997";
}
.ci-Code:before {
  content: "\e998";
}
.ci-Coffe_To_Go:before {
  content: "\e999";
}
.ci-Coffee:before {
  content: "\e99a";
}
.ci-Columns:before {
  content: "\e99b";
}
.ci-Combine_Cells:before {
  content: "\e99c";
}
.ci-Command:before {
  content: "\e99d";
}
.ci-Compass:before {
  content: "\e99e";
}
.ci-Cookie:before {
  content: "\e99f";
}
.ci-Copy:before {
  content: "\e9a0";
}
.ci-Credit_Card_01:before {
  content: "\e9a1";
}
.ci-Credit_Card_02:before {
  content: "\e9a2";
}
.ci-Crop:before {
  content: "\e9a3";
}
.ci-Cupcake:before {
  content: "\e9a4";
}
.ci-Cylinder:before {
  content: "\e9a5";
}
.ci-Data:before {
  content: "\e9a6";
}
.ci-Delete_Column:before {
  content: "\e9a7";
}
.ci-Delete_Row:before {
  content: "\e9a8";
}
.ci-Desktop_Tower:before {
  content: "\e9a9";
}
.ci-Desktop:before {
  content: "\e9aa";
}
.ci-Devices:before {
  content: "\e9ab";
}
.ci-Double_Quotes_L:before {
  content: "\e9ac";
}
.ci-Double_Quotes_R:before {
  content: "\e9ad";
}
.ci-Download_Package:before {
  content: "\e9ae";
}
.ci-Download:before {
  content: "\e9af";
}
.ci-Drag_Horizontal:before {
  content: "\e9b0";
}
.ci-Drag_Vertical:before {
  content: "\e9b1";
}
.ci-Dummy_Circle_Small:before {
  content: "\e9b2";
}
.ci-Dummy_Circle:before {
  content: "\e9b3";
}
.ci-Dummy_Square_Small:before {
  content: "\e9b4";
}
.ci-Dummy_Square:before {
  content: "\e9b5";
}
.ci-Edit_Pencil_01:before {
  content: "\e9b6";
}
.ci-Edit_Pencil_02:before {
  content: "\e9b7";
}
.ci-Edit_Pencil_Line_01:before {
  content: "\e9b8";
}
.ci-Edit_Pencil_Line_02:before {
  content: "\e9b9";
}
.ci-Exit:before {
  content: "\e9ba";
}
.ci-Expand:before {
  content: "\e9bb";
}
.ci-External_Link:before {
  content: "\e9bc";
}
.ci-Figma:before {
  content: "\e9bd";
}
.ci-File_Add:before {
  content: "\e9be";
}
.ci-File_Blank:before {
  content: "\e9bf";
}
.ci-File_Check:before {
  content: "\e9c0";
}
.ci-File_Close:before {
  content: "\e9c1";
}
.ci-File_Code:before {
  content: "\e9c2";
}
.ci-File_Document:before {
  content: "\e9c3";
}
.ci-File_Download:before {
  content: "\e9c4";
}
.ci-File_Edit:before {
  content: "\e9c5";
}
.ci-File_Remove:before {
  content: "\e9c6";
}
.ci-File_Search:before {
  content: "\e9c7";
}
.ci-File_Upload:before {
  content: "\e9c8";
}
.ci-Files:before {
  content: "\e9c9";
}
.ci-Filter_Off:before {
  content: "\e9ca";
}
.ci-Filter:before {
  content: "\e9cb";
}
.ci-First_Aid:before {
  content: "\e9cc";
}
.ci-Flag:before {
  content: "\e9cd";
}
.ci-Folder_Add:before {
  content: "\e9ce";
}
.ci-Folder_Check:before {
  content: "\e9cf";
}
.ci-Folder_Close:before {
  content: "\e9d0";
}
.ci-Folder_Code:before {
  content: "\e9d1";
}
.ci-Folder_Document:before {
  content: "\e9d2";
}
.ci-Folder_Download:before {
  content: "\e9d3";
}
.ci-Folder_Edit:before {
  content: "\e9d4";
}
.ci-Folder_Open:before {
  content: "\e9d5";
}
.ci-Folder_Remove:before {
  content: "\e9d6";
}
.ci-Folder_Search:before {
  content: "\e9d7";
}
.ci-Folder_Upload:before {
  content: "\e9d8";
}
.ci-Folder:before {
  content: "\e9d9";
}
.ci-Folders:before {
  content: "\e9da";
}
.ci-Font:before {
  content: "\e9db";
}
.ci-Forward:before {
  content: "\e9dc";
}
.ci-Gift:before {
  content: "\e9dd";
}
.ci-Globe:before {
  content: "\e9de";
}
.ci-Hamburger_LG:before {
  content: "\e9df";
}
.ci-Hamburger_MD:before {
  content: "\e9e0";
}
.ci-Handbag:before {
  content: "\e9e1";
}
.ci-Heading_H1:before {
  content: "\e9e2";
}
.ci-Heading_H2:before {
  content: "\e9e3";
}
.ci-Heading_H3:before {
  content: "\e9e4";
}
.ci-Heading_H4:before {
  content: "\e9e5";
}
.ci-Heading_H5:before {
  content: "\e9e6";
}
.ci-Heading_H6:before {
  content: "\e9e7";
}
.ci-Heading:before {
  content: "\e9e8";
}
.ci-Headphones:before {
  content: "\e9e9";
}
.ci-Heart_01:before {
  content: "\e9ea";
}
.ci-Heart_02:before {
  content: "\e9eb";
}
.ci-Help:before {
  content: "\e9ec";
}
.ci-Hide:before {
  content: "\e9ed";
}
.ci-House_01:before {
  content: "\e9ee";
}
.ci-House_02:before {
  content: "\e9ef";
}
.ci-House_03:before {
  content: "\e9f0";
}
.ci-House_Add:before {
  content: "\e9f1";
}
.ci-House_Check:before {
  content: "\e9f2";
}
.ci-House_Close:before {
  content: "\e9f3";
}
.ci-House_Remove:before {
  content: "\e9f4";
}
.ci-Image_01:before {
  content: "\e9f5";
}
.ci-Image_02:before {
  content: "\e9f6";
}
.ci-Info:before {
  content: "\e9f7";
}
.ci-Instance:before {
  content: "\e9f8";
}
.ci-Italic:before {
  content: "\e9f9";
}
.ci-Keyboard:before {
  content: "\e9fa";
}
.ci-Label:before {
  content: "\e9fb";
}
.ci-Laptop:before {
  content: "\e9fc";
}
.ci-Layer:before {
  content: "\e9fd";
}
.ci-Layers:before {
  content: "\e9fe";
}
.ci-Leaf:before {
  content: "\e9ff";
}
.ci-Line_L:before {
  content: "\ea00";
}
.ci-Line_M:before {
  content: "\ea01";
}
.ci-Line_S:before {
  content: "\ea02";
}
.ci-Line_Xl:before {
  content: "\ea03";
}
.ci-Link_Break:before {
  content: "\ea04";
}
.ci-Link_Horizontal_Off:before {
  content: "\ea05";
}
.ci-Link_Horizontal:before {
  content: "\ea06";
}
.ci-Link_Vertical:before {
  content: "\ea07";
}
.ci-Link:before {
  content: "\ea08";
}
.ci-List_Add:before {
  content: "\ea09";
}
.ci-List_Check:before {
  content: "\ea0a";
}
.ci-List_Checklist:before {
  content: "\ea0b";
}
.ci-List_Ordered:before {
  content: "\ea0c";
}
.ci-List_Remove:before {
  content: "\ea0d";
}
.ci-List_Unordered:before {
  content: "\ea0e";
}
.ci-Loading:before {
  content: "\ea0f";
}
.ci-Lock_Open:before {
  content: "\ea10";
}
.ci-Lock:before {
  content: "\ea11";
}
.ci-Log_Out:before {
  content: "\ea12";
}
.ci-Magnifying_Glass_Minus:before {
  content: "\ea13";
}
.ci-Magnifying_Glass_Plus:before {
  content: "\ea14";
}
.ci-Mail_Open:before {
  content: "\ea15";
}
.ci-Mail:before {
  content: "\ea16";
}
.ci-Main_Component:before {
  content: "\ea17";
}
.ci-Map_Pin:before {
  content: "\ea18";
}
.ci-Map:before {
  content: "\ea19";
}
.ci-Mention:before {
  content: "\ea1a";
}
.ci-Menu_Alt_01:before {
  content: "\ea1b";
}
.ci-Menu_Alt_02:before {
  content: "\ea1c";
}
.ci-Menu_Alt_03:before {
  content: "\ea1d";
}
.ci-Menu_Alt_04:before {
  content: "\ea1e";
}
.ci-Menu_Alt_05:before {
  content: "\ea1f";
}
.ci-Menu_Duo_LG:before {
  content: "\ea20";
}
.ci-Menu_Duo_MD:before {
  content: "\ea21";
}
.ci-Mobile_Button:before {
  content: "\ea22";
}
.ci-Mobile:before {
  content: "\ea23";
}
.ci-Monitor_Play:before {
  content: "\ea24";
}
.ci-Monitor:before {
  content: "\ea25";
}
.ci-Moon:before {
  content: "\ea26";
}
.ci-More_Grid_Big:before {
  content: "\ea27";
}
.ci-More_Grid_Small:before {
  content: "\ea28";
}
.ci-More_Horizontal:before {
  content: "\ea29";
}
.ci-More_Vertical:before {
  content: "\ea2a";
}
.ci-Mouse:before {
  content: "\ea2b";
}
.ci-Move_Horizontal:before {
  content: "\ea2c";
}
.ci-Move_Vertical:before {
  content: "\ea2d";
}
.ci-Move:before {
  content: "\ea2e";
}
.ci-Moving_Desk:before {
  content: "\ea2f";
}
.ci-Navigation:before {
  content: "\ea30";
}
.ci-Note_Edit:before {
  content: "\ea31";
}
.ci-Note_Search:before {
  content: "\ea32";
}
.ci-Note:before {
  content: "\ea33";
}
.ci-Notebook:before {
  content: "\ea34";
}
.ci-Octagon_Check:before {
  content: "\ea35";
}
.ci-Octagon_Help:before {
  content: "\ea36";
}
.ci-Octagon_Warning:before {
  content: "\ea37";
}
.ci-Octagon:before {
  content: "\ea38";
}
.ci-Option:before {
  content: "\ea39";
}
.ci-Paper_Plane:before {
  content: "\ea3a";
}
.ci-Paperclip_Attechment_Horizontal:before {
  content: "\ea3b";
}
.ci-Paperclip_Attechment_Tilt:before {
  content: "\ea3c";
}
.ci-Paragraph:before {
  content: "\ea3d";
}
.ci-Path:before {
  content: "\ea3e";
}
.ci-Pause_Circle:before {
  content: "\ea3f";
}
.ci-Pause:before {
  content: "\ea40";
}
.ci-Phone:before {
  content: "\ea41";
}
.ci-Planet:before {
  content: "\ea42";
}
.ci-Play_Circle:before {
  content: "\ea43";
}
.ci-Play:before {
  content: "\ea44";
}
.ci-Printer:before {
  content: "\ea45";
}
.ci-Puzzle:before {
  content: "\ea46";
}
.ci-Qr_Code:before {
  content: "\ea47";
}
.ci-Radio_Fill:before {
  content: "\ea48";
}
.ci-Radio_Unchecked:before {
  content: "\ea49";
}
.ci-Rainbow:before {
  content: "\ea4a";
}
.ci-Redo:before {
  content: "\ea4b";
}
.ci-Remove_Minus_Circle:before {
  content: "\ea4c";
}
.ci-Remove_Minus:before {
  content: "\ea4d";
}
.ci-Rewind:before {
  content: "\ea4e";
}
.ci-Rows:before {
  content: "\ea4f";
}
.ci-Ruler:before {
  content: "\ea50";
}
.ci-Save:before {
  content: "\ea51";
}
.ci-Search_Magnifying_Glass:before {
  content: "\ea52";
}
.ci-Select_Multiple:before {
  content: "\ea53";
}
.ci-Settings_Future:before {
  content: "\ea54";
}
.ci-Settings:before {
  content: "\ea55";
}
.ci-Share_Android:before {
  content: "\ea56";
}
.ci-Share_iOS_Export:before {
  content: "\ea57";
}
.ci-Shield_Check:before {
  content: "\ea58";
}
.ci-Shield_Warning:before {
  content: "\ea59";
}
.ci-Shield:before {
  content: "\ea5a";
}
.ci-Shopping_Bag_01:before {
  content: "\ea5b";
}
.ci-Shopping_Bag_02:before {
  content: "\ea5c";
}
.ci-Shopping_Cart_01:before {
  content: "\ea5d";
}
.ci-Shopping_Cart_02:before {
  content: "\ea5e";
}
.ci-Show:before {
  content: "\ea5f";
}
.ci-Shrink:before {
  content: "\ea60";
}
.ci-Shuffle:before {
  content: "\ea61";
}
.ci-Single_Quotes_L:before {
  content: "\ea62";
}
.ci-Single_Quotes_R:before {
  content: "\ea63";
}
.ci-Skip_Back:before {
  content: "\ea64";
}
.ci-Skip_Forward:before {
  content: "\ea65";
}
.ci-Slider_01:before {
  content: "\ea66";
}
.ci-Slider_02:before {
  content: "\ea67";
}
.ci-Slider_03:before {
  content: "\ea68";
}
.ci-Sort_Ascending:before {
  content: "\ea69";
}
.ci-Sort_Descending:before {
  content: "\ea6a";
}
.ci-Square_Check:before {
  content: "\ea6b";
}
.ci-Square_Help:before {
  content: "\ea6c";
}
.ci-Square_Warning:before {
  content: "\ea6d";
}
.ci-Square:before {
  content: "\ea6e";
}
.ci-Star:before {
  content: "\ea6f";
}
.ci-Stop_Circle:before {
  content: "\ea70";
}
.ci-Stop_Sign:before {
  content: "\ea71";
}
.ci-Stop:before {
  content: "\ea72";
}
.ci-Strikethrough:before {
  content: "\ea73";
}
.ci-Suitcase:before {
  content: "\ea74";
}
.ci-Sun:before {
  content: "\ea75";
}
.ci-Swatches_Palette:before {
  content: "\ea76";
}
.ci-Swicht_Left:before {
  content: "\ea77";
}
.ci-Swicht_Right:before {
  content: "\ea78";
}
.ci-Table_Add:before {
  content: "\ea79";
}
.ci-Table_Remove:before {
  content: "\ea7a";
}
.ci-Table:before {
  content: "\ea7b";
}
.ci-Tablet_Button:before {
  content: "\ea7c";
}
.ci-Tablet:before {
  content: "\ea7d";
}
.ci-Tag:before {
  content: "\ea7e";
}
.ci-Terminal:before {
  content: "\ea7f";
}
.ci-Text_Align_Center:before {
  content: "\ea80";
}
.ci-Text_Align_Justify:before {
  content: "\ea81";
}
.ci-Text_Align_Left:before {
  content: "\ea82";
}
.ci-Text_Align_Right:before {
  content: "\ea83";
}
.ci-Text:before {
  content: "\ea84";
}
.ci-Ticket_Voucher:before {
  content: "\ea85";
}
.ci-Timer_Add:before {
  content: "\ea86";
}
.ci-Timer_Close:before {
  content: "\ea87";
}
.ci-Timer_Remove:before {
  content: "\ea88";
}
.ci-Timer:before {
  content: "\ea89";
}
.ci-Trash_Empty:before {
  content: "\ea8a";
}
.ci-Trash_Full:before {
  content: "\ea8b";
}
.ci-Trending_Down:before {
  content: "\ea8c";
}
.ci-Trending_Up:before {
  content: "\ea8d";
}
.ci-Triangle_Check:before {
  content: "\ea8e";
}
.ci-Triangle_Warning:before {
  content: "\ea8f";
}
.ci-Triangle:before {
  content: "\ea90";
}
.ci-Underline:before {
  content: "\ea91";
}
.ci-Undo:before {
  content: "\ea92";
}
.ci-Unfold_Less:before {
  content: "\ea93";
}
.ci-Unfold_More:before {
  content: "\ea94";
}
.ci-User_01:before {
  content: "\ea95";
}
.ci-User_02:before {
  content: "\ea96";
}
.ci-User_03:before {
  content: "\ea97";
}
.ci-User_Add:before {
  content: "\ea98";
}
.ci-User_Card_ID:before {
  content: "\ea99";
}
.ci-User_Check:before {
  content: "\ea9a";
}
.ci-User_Circle:before {
  content: "\ea9b";
}
.ci-User_Close:before {
  content: "\ea9c";
}
.ci-User_Remove:before {
  content: "\ea9d";
}
.ci-User_Square:before {
  content: "\ea9e";
}
.ci-User_Voice:before {
  content: "\ea9f";
}
.ci-Users_Group:before {
  content: "\eaa0";
}
.ci-Users:before {
  content: "\eaa1";
}
.ci-Volume_Max:before {
  content: "\eaa2";
}
.ci-Volume_Min:before {
  content: "\eaa3";
}
.ci-Volume_Minus:before {
  content: "\eaa4";
}
.ci-Volume_Off_02:before {
  content: "\eaa5";
}
.ci-Volume_Off:before {
  content: "\eaa6";
}
.ci-Volume_Plus:before {
  content: "\eaa7";
}
.ci-Warning:before {
  content: "\eaa8";
}
.ci-Water_Drop:before {
  content: "\eaa9";
}
.ci-Wavy_Check:before {
  content: "\eaaa";
}
.ci-Wavy_Help:before {
  content: "\eaab";
}
.ci-Wavy_Warning:before {
  content: "\eaac";
}
.ci-Wavy:before {
  content: "\eaad";
}
.ci-Wifi_High:before {
  content: "\eaae";
}
.ci-Wifi_Low:before {
  content: "\eaaf";
}
.ci-Wifi_Medium:before {
  content: "\eab0";
}
.ci-Wifi_None:before {
  content: "\eab1";
}
.ci-Wifi_Off:before {
  content: "\eab2";
}
.ci-Wifi_Problem:before {
  content: "\eab3";
}
.ci-Window_Check:before {
  content: "\eab4";
}
.ci-Window_Close:before {
  content: "\eab5";
}
.ci-Window_Code_Block:before {
  content: "\eab6";
}
.ci-Window_Sidebar:before {
  content: "\eab7";
}
.ci-Window_Terminal:before {
  content: "\eab8";
}
.ci-Window:before {
  content: "\eab9";
}

```

### File: `packages/magic-backup-importer/app/database/DatabaseManager.ts`
```ts
import type { IDBPDatabase } from "idb";
import { openDatabase } from "./connection";
import type { Schema } from "./schema";

export class DatabaseManager {
  initialized: Promise<void>;
  database!: IDBPDatabase<Schema>;

  persisted = true;
  persistenceMessageDismissed = false;

  constructor() {
    let markAsInitialized: () => void;
    this.initialized = new Promise((resolve) => {
      markAsInitialized = resolve;
    });

    if (typeof window === "undefined") return;

    if ("storage" in navigator) {
      navigator.storage
        .persisted()
        .then((persisted) => {
          this.persisted = persisted;
        })
        .catch(() => {});
    }

    openDatabase()
      .then((database) => {
        this.database = database;
        markAsInitialized();
      })
      .catch((error) => {
        console.error("Failed to open database:", error);
      });
  }

  async requestPersistence() {
    if ("chrome" in window) {
      await Notification.requestPermission();
    }

    if ("storage" in navigator) {
      this.persisted = await navigator.storage.persist();
    }
  }

  get shouldShowPersistenceWarning() {
    return !this.persisted && !this.persistenceMessageDismissed;
  }
}

```

### File: `packages/magic-backup-importer/app/database/DatabaseManagerContext.ts`
```ts
import { createContext } from "react";
import type { DatabaseManager } from "./DatabaseManager";

export const DatabaseManagerContext = createContext<DatabaseManager | null>(
  null,
);

DatabaseManagerContext.displayName = "DatabaseManagerContext";

export const DatabaseManagerProvider = DatabaseManagerContext.Provider;

```

### File: `packages/magic-backup-importer/app/database/connection.ts`
```ts
import { type IDBPDatabase, type IDBPTransaction, openDB } from "idb";
import type { Schema } from "./schema";
import { showUpgradeBlockedMessage } from "./showUpgradeBlockedMessage";
import { upgradeDatabase } from "./upgradeDatabase";

export const openDatabase = async () => {
  return openDB<Schema>("discohook", 10, {
    // biome-ignore lint/correctness/noUnusedFunctionParameters: Too scared to change any of this code
    upgrade: (database, oldVersion, newVersion, transaction) => {
      // Casting to unknown schema, because upgrades shouldn't assume how the
      // schema looks at that time
      upgradeDatabase(
        database as IDBPDatabase,
        transaction as IDBPTransaction<unknown, string[], "versionchange">,
        oldVersion,
      )
        .then(() => {
          localStorage.setItem("database-upgraded-version", "10");
          document.querySelector("#db-upgrade-blocked")?.remove();
        })
        .catch((error: Error) => {
          console.error("Error on database upgrade:", error);
        });
    },
    blocked: showUpgradeBlockedMessage,
  });
};

```

### File: `packages/magic-backup-importer/app/database/schema.ts`
```ts
export interface Backup {
  id: number;
  name: string;
  messages: Array<unknown>;
  targets: { url: string }[];
}

export type Schema = {
  backup: {
    key: number;
    value: Backup;
    indexes: {
      name: string;
    };
  };
};

```

### File: `packages/magic-backup-importer/app/database/showUpgradeBlockedMessage.ts`
```ts
export const showUpgradeBlockedMessage = () => {
  const container = document.createElement("div");
  container.id = "db-upgrade-blocked";
  container.style.position = "absolute";
  container.style.top = "0";
  container.style.right = "0";
  container.style.bottom = "0";
  container.style.left = "0";
  container.style.background = "rgba(0, 0, 0, 0.85)";
  container.style.padding = "16px";

  const header = document.createElement("h1");
  header.style.color = "#ffffff";
  header.append("Discohook's local database needs an upgrade");

  const blockedMessage = document.createElement("p");
  blockedMessage.append(
    "However, the upgrade can't proceed because there are older sessions of Discohook open.",
  );

  const closeTabsMessage = document.createElement("p");
  closeTabsMessage.append("Please close all Discohook tabs before continuing.");

  // @ts-expect-error
  container.append(header, blockedMessage, closeTabsMessage);
  // @ts-expect-error
  document.body.append(container);
};

```

### File: `packages/magic-backup-importer/app/database/upgradeDatabase.ts`
```ts
import type { IDBPDatabase, IDBPTransaction } from "idb";

const isObject = (value: unknown) =>
  typeof value === "object" && value !== null;

export const mapKeys = (
  object: unknown,
  fn: (key: string) => string,
): Record<string, unknown> | unknown[] => {
  if (Array.isArray(object)) {
    return object.map((value) =>
      isObject(value) ? mapKeys(value, fn) : value,
    );
  }

  const result: Record<string, unknown> = {};

  for (const [key, value] of Object.entries(
    object as Record<string, unknown>,
  )) {
    if (isObject(value)) {
      result[fn(key)] = mapKeys(value, fn);
    } else {
      result[fn(key)] = value;
    }
  }

  return result;
};

const toSnakeCase = (object: unknown) =>
  mapKeys(object, (key) =>
    key.replace(/[A-Z]/g, (match) => `_${match.toLowerCase()}`),
  );

export const upgradeDatabase = async (
  database: IDBPDatabase,
  transaction: IDBPTransaction<unknown, string[], "versionchange">,
  oldVersion: number,
) => {
  if (oldVersion < 2 && oldVersion >= 1) {
    let cursor = await transaction.objectStore("backups").openCursor();

    while (cursor) {
      await cursor.update({
        name: cursor.key,
        message: cursor.value,
      });

      cursor = await cursor.continue();
    }
  }

  if (oldVersion < 3) {
    database.createObjectStore("backup", {
      keyPath: "id",
      autoIncrement: true,
    });

    const backupStore = transaction.objectStore("backup");
    backupStore.createIndex("name", "name", {
      unique: true,
    });
  }

  if (oldVersion < 4 && oldVersion >= 1) {
    const backupStore = transaction.objectStore("backup");

    const existingBackups = new Set<IDBValidKey>();
    let nameCursor = await backupStore.index("name").openKeyCursor();

    while (nameCursor) {
      existingBackups.add(nameCursor.key);
      nameCursor = await nameCursor.continue();
    }

    let cursor = await transaction.objectStore("backups").openCursor();

    while (cursor) {
      if (!existingBackups.has(cursor.key)) {
        await backupStore.put({
          ...cursor.value,
          name: cursor.key,
          message: toSnakeCase(cursor.value.message),
        });
      }

      cursor = await cursor.continue();
    }
  }

  if (oldVersion < 5 && oldVersion >= 1) {
    const backupStore = transaction.objectStore("backup");

    let cursor = await backupStore.openCursor();

    while (cursor) {
      const { message, ...rest } = cursor.value;

      await backupStore.put({
        ...rest,
        messages: [message],
      });

      cursor = await cursor.continue();
    }
  }

  if (oldVersion < 6 && oldVersion >= 1) {
    const backupStore = transaction.objectStore("backup");

    let cursor = await backupStore.openCursor();

    while (cursor) {
      const { webhookUrl, ...rest } = cursor.value;

      await backupStore.put({
        ...rest,
        target: {
          url: webhookUrl,
        },
      });

      cursor = await cursor.continue();
    }
  }

  if (oldVersion < 9 && oldVersion >= 1) {
    const backupStore = transaction.objectStore("backup");

    let cursor = await backupStore.openCursor();

    while (cursor) {
      const { id, name, messages, target } = cursor.value;

      if (name) {
        await backupStore.put({
          id,
          name,
          messages: messages.map((data: Record<string, unknown>) => ({
            data: "data" in data ? data.data : data,
            reference: "reference" in data ? data.reference : target.message,
          })),
          target: {
            url: target.url,
          },
        });
      } else {
        await backupStore.delete(id);
      }

      cursor = await cursor.continue();
    }
  }

  if (oldVersion < 10 && oldVersion >= 1) {
    const backupStore = transaction.objectStore("backup");

    let cursor = await backupStore.openCursor();

    while (cursor) {
      const { target, ...backup } = cursor.value;

      await backupStore.put({
        ...backup,
        targets: [{ url: target.url ?? "" }],
      });

      cursor = await cursor.continue();
    }
  }
};

```

### File: `packages/magic-backup-importer/app/entry.client.tsx`
```tsx
/**
 * By default, Remix will handle hydrating your app on the client for you.
 * You are free to delete this file if you'd like to, but if you ever want it revealed again, you can run `npx remix reveal` ✨
 * For more information, see https://remix.run/file-conventions/entry.client
 */

import { RemixBrowser } from "@remix-run/react";
import { StrictMode, startTransition } from "react";
import { hydrateRoot } from "react-dom/client";

startTransition(() => {
  hydrateRoot(
    document,
    <StrictMode>
      <RemixBrowser />
    </StrictMode>,
  );
});

```

### File: `packages/magic-backup-importer/app/entry.server.tsx`
```tsx
/**
 * By default, Remix will handle generating the HTTP Response for you.
 * You are free to delete this file if you'd like to, but if you ever want it revealed again, you can run `npx remix reveal` ✨
 * For more information, see https://remix.run/file-conventions/entry.server
 */

import type { EntryContext } from "@remix-run/cloudflare";
import { RemixServer } from "@remix-run/react";
import { isbot } from "isbot";
import { renderToReadableStream } from "react-dom/server";

export default async function handleRequest(
  request: Request,
  responseStatusCode: number,
  responseHeaders: Headers,
  remixContext: EntryContext,
) {
  let status = responseStatusCode;
  const body = await renderToReadableStream(
    <RemixServer context={remixContext} url={request.url} />,
    {
      signal: request.signal,
      onError(error: unknown) {
        // Log streaming rendering errors from inside the shell
        console.error(error);
        status = 500;
      },
    },
  );

  if (isbot(request.headers.get("user-agent") || "")) {
    await body.allReady;
  }

  responseHeaders.set("Content-Type", "text/html");
  return new Response(body, {
    headers: responseHeaders,
    status,
  });
}

```

### File: `packages/magic-backup-importer/app/root.tsx`
```tsx
import type { LinksFunction } from "@remix-run/cloudflare";
import { cssBundleHref } from "@remix-run/css-bundle";
import {
  Links,
  LiveReload,
  Meta,
  Outlet,
  Scripts,
  ScrollRestoration,
} from "@remix-run/react";
import coolicons from "~/coolicons.css";
import stylesheet from "~/tailwind.css";

export const links: LinksFunction = () => [
  ...(cssBundleHref ? [{ rel: "stylesheet", href: cssBundleHref }] : []),
  { rel: "stylesheet", href: stylesheet },
  { rel: "stylesheet", href: coolicons },
];

export default function App() {
  return (
    <html lang="en">
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <Meta />
        <Links />
      </head>
      <body className="bg-white text-black dark:bg-primary-600 dark:text-primary-230">
        <Outlet />
        <ScrollRestoration />
        <Scripts />
        <LiveReload />
      </body>
    </html>
  );
}

```

### File: `packages/magic-backup-importer/app/routes/_index.tsx`
```tsx
import { redirect } from "@remix-run/cloudflare";
import type { LoaderArgs } from "./migrate";

export const loader = async ({ request, context }: LoaderArgs) => {
  const url = new URL(request.url);
  const origin = new URL(context.env.DISCOHOOK_ORIGIN);
  url.protocol = origin.protocol;
  url.host = origin.host;
  url.searchParams.set("m", "org");
  return redirect(url.href);
};

```

### File: `packages/magic-backup-importer/app/routes/migrate.tsx`
```tsx
import { type MetaFunction, redirect } from "@remix-run/cloudflare";
import { useLoaderData } from "@remix-run/react";
import type { LoaderFunctionArgs as RRLoaderFunctionArgs } from "@remix-run/router";
import { useEffect, useReducer, useState } from "react";
import { Button, ButtonStyle } from "~/components/Button";
import { Checkbox } from "~/components/Checkbox";
import { DatabaseManager } from "~/database/DatabaseManager";
import type { Backup } from "~/database/schema";
import { getLocalStorage } from "~/util/storage";

const getAllBackups = async (manager: DatabaseManager) => {
  const backups: Backup[] = [];

  let cursor = await manager.database
    .transaction("backup")
    .objectStore("backup")
    .openCursor();

  while (cursor) {
    backups.push(cursor.value);
    cursor = await cursor.continue();
  }
  return backups;
};

export interface Context {
  env: {
    DISCOHOOK_ORIGIN: string;
  };
}

// Just for debug, call this manually to store a backup
// biome-ignore lint/correctness/noUnusedVariables: ^
const saveBackup = async (manager: DatabaseManager) => {
  await manager.database.clear("backup");
  await manager.database
    .transaction("backup", "readwrite")
    .objectStore("backup")
    .put({
      id: 1,
      name: "Magic",
      messages: [
        {
          data: {
            content: "Content",
            embeds: [
              {
                thumbnail: {
                  url: "https://cdn.discordapp.com/avatars/633565743103082527/fa47564fcd19857e833e97c6c0208966.webp",
                },
              },
            ],
          },
        },
      ],
      targets: [],
    });
};

export type LoaderArgs = RRLoaderFunctionArgs<Context> & { context: Context };

export const loader = async ({ request, context }: LoaderArgs) => {
  const params = new URL(request.url).searchParams;
  const token = params.get("token");
  if (!token) {
    return redirect(`${context.env.DISCOHOOK_ORIGIN}/?m=org&${params}`);
  }
  return { token, origin: context.env.DISCOHOOK_ORIGIN };
};

export const meta: MetaFunction = () => {
  return [{ title: "Discohook" }];
};

interface TokenUserInfo {
  name: string;
  avatarUrl: string;
  backups: { name: string }[];
}

export default function Index() {
  const { token, origin } = useLoaderData<typeof loader>();
  const { settings } = getLocalStorage();

  const [error, setError] = useState<string>();
  const [user, setUser] = useState<TokenUserInfo>();
  const [backups, setBackups] = useState<Backup[]>();
  const [selected, updateSelected] = useReducer(
    (d: Record<string, boolean>, partialD: Record<string, boolean>) => ({
      ...d,
      ...partialD,
    }),
    {},
  );

  useEffect(() => {
    (async () => {
      const response = await fetch(`${origin}/api/v1/magic-backups`, {
        method: "GET",
        headers: {
          "X-Discohook-Pixiedust": token,
        },
      });
      if (!response.ok) {
        console.error(response);
        const { message } = (await response.json()) as { message: string };
        setError(message);
        return;
      }
      const data = (await response.json()) as TokenUserInfo;
      setUser(data);

      const databaseManager = new DatabaseManager();
      await databaseManager.initialized;
      // await saveBackup(databaseManager);

      const localBackups = await getAllBackups(databaseManager);
      console.log(localBackups);
      setBackups(localBackups);
      const backupNames = data.backups.map((b) => b.name);
      updateSelected(
        Object.fromEntries(
          localBackups.map((b) => [b.id, !backupNames.includes(b.name)]),
        ),
      );
    })();
  }, [token, origin]);

  return (
    <div className="p-8 h-screen flex flex-col">
      <div className="max-w-xl m-auto">
        {error && (
          <p className="rounded-lg px-4 py-2 bg-red-400 text-black">
            <span className="font-semibold">You've encountered an error:</span>
            <br />
            {error}
          </p>
        )}
        {user && backups ? (
          <>
            <div className="p-4 rounded-lg bg-gray-900 shadow-md">
              <div className="flex">
                <img
                  src={user.avatarUrl}
                  className="rounded-full my-auto h-8 mr-2"
                  alt={user.name}
                />
                <p className="my-auto text-lg font-medium">
                  Hi <span className="font-semibold">{user.name}</span>!
                </p>
              </div>
              <div className="mt-2">
                {backups.length === 0 ? (
                  <p>You don't seem to have any backups.</p>
                ) : (
                  <div>
                    <p>
                      Below are all backups that are stored on this browser.
                      Please deselect the backups that you would not like to
                      import. If you are unsure, just keep all checked.
                    </p>
                    <div className="mt-2 space-y-1 max-h-96 overflow-y-auto">
                      {backups.map((backup) => (
                        <Checkbox
                          key={`backup-${backup.id}`}
                          label={
                            <span
                              className={
                                user.backups
                                  .map((b) => b.name)
                                  .includes(backup.name)
                                  ? "text-red-400"
                                  : ""
                              }
                            >
                              {backup.name}
                            </span>
                          }
                          checked={selected[backup.id] ?? true}
                          onChange={(e) =>
                            updateSelected({
                              [backup.id]: e.currentTarget.checked,
                            })
                          }
                        />
                      ))}
                    </div>
                    {backups.filter((b) =>
                      user.backups.map((ub) => ub.name).includes(b.name),
                    ).length !== 0 && (
                      <p className="mt-2 text-sm text-gray-500">
                        Backup names in{" "}
                        <span className="text-red-400">red</span> indicate that
                        you already have a cloud backup with that name. You can
                        choose to import them anyway by simply ticking the box.
                      </p>
                    )}
                  </div>
                )}
              </div>
            </div>
            <div className="mt-2 grid grid-cols-3">
              <div className="flex">
                <a className="mr-auto" href={`${origin}/me/backups`}>
                  <Button discordStyle={ButtonStyle.Secondary}>
                    <span className="m-auto">
                      <i className="ci-Chevron_Left" /> Back
                    </span>
                  </Button>
                </a>
              </div>
              <div className="flex">
                <Button
                  className="mx-auto"
                  disabled={
                    Object.values(selected).filter(Boolean).length === 0
                  }
                  onClick={async () => {
                    if (!backups) return;
                    const response = await fetch(
                      `${origin}/api/v1/magic-backups`,
                      {
                        method: "POST",
                        body: JSON.stringify({
                          backups: backups.filter(
                            (b) => selected[b.id] !== false,
                          ),
                        }),
                        headers: {
                          "Content-Type": "application/json",
                          "X-Discohook-Pixiedust": token,
                        },
                      },
                    );
                    if (!response.ok) {
                      console.error(response);
                      const { message } = (await response.json()) as {
                        message: string;
                      };
                      setError(message);
                      return;
                    }
                    const url = new URL(`${origin}/me/backups`);
                    if (settings) {
                      url.searchParams.set(
                        "settings",
                        JSON.stringify(settings),
                      );
                    }
                    window.location.href = url.href;
                  }}
                >
                  <span className="m-auto">Finish</span>
                </Button>
              </div>
              <div className="flex">
                <Button
                  className="ml-auto"
                  discordStyle={ButtonStyle.Secondary}
                  disabled={backups.length === 0}
                  onClick={() => {
                    // Borrowing all this from site/app/modals/JsonEditorModal
                    const blob = new Blob(
                      [JSON.stringify({ version: 7, backups })],
                      { type: "application/json" },
                    );
                    const blobUrl = URL.createObjectURL(blob);
                    try {
                      const link = document.createElement("a");
                      link.href = blobUrl;
                      link.download = "backups.json";
                      link.click();
                    } finally {
                      URL.revokeObjectURL(blobUrl);
                    }
                  }}
                >
                  <span className="m-auto">Export All</span>
                </Button>
              </div>
            </div>
          </>
        ) : (
          <img
            src={`${origin}/logos/icon.svg`}
            alt="Discohook"
            className="h-32 animate-pulse m-auto"
          />
        )}
      </div>
    </div>
  );
}

```

### File: `packages/magic-backup-importer/app/tailwind.css`
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@font-face {
  font-family: Whitney;
  font-style: normal;
  font-weight: 300;
  src: url(/fonts/whitney-300.woff), url(/fonts/whitney-300.woff2);
  font-display: swap;
}

@font-face {
  font-family: Whitney;
  font-style: normal;
  font-weight: 400;
  src: url(/fonts/whitney-400.woff), url(/fonts/whitney-400.woff2);
  font-display: swap;
}

@font-face {
  font-family: Whitney;
  font-style: normal;
  font-weight: 500;
  src: url(/fonts/whitney-500.woff), url(/fonts/whitney-500.woff2);
  font-display: swap;
}

@font-face {
  font-family: Whitney;
  font-style: normal;
  font-weight: 600;
  src: url(/fonts/whitney-600.woff), url(/fonts/whitney-600.woff2);
  font-display: swap;
}

@font-face {
  font-family: Whitney;
  font-style: normal;
  font-weight: 700;
  src: url(/fonts/whitney-700.woff), url(/fonts/whitney-700.woff2);
  font-display: swap;
}

```

### File: `packages/magic-backup-importer/app/util/storage.ts`
```ts
export interface Settings {
  theme?: "light" | "dark";
  display?: "cozy" | "compact";
  fontSize?: number;
  confirmExit?: boolean;
  expandSections?: boolean;
}

export interface LocalStorage {
  settings?: Settings;
  databaseUpgradedVersion?: string;
}

export const getLocalStorage = (): LocalStorage => {
  try {
    localStorage;
  } catch {
    return {};
  }

  const settings = JSON.parse(
    localStorage.getItem("settings") ?? "{}",
  ) as Settings;
  const databaseUpgradedVersion =
    localStorage.getItem("database-upgraded-version") || undefined;

  return { settings, databaseUpgradedVersion };
};

```

### File: `packages/magic-backup-importer/package.json`
```json
{
  "name": "magic-backup-importer",
  "private": true,
  "sideEffects": false,
  "type": "module",
  "installConfig": {
    "hoistingLimits": "workspaces"
  },
  "scripts": {
    "build": "remix build",
    "deploy": "wrangler deploy",
    "deploy-preview": "wrangler deploy --env=preview",
    "dev": "remix dev --manual -c \"npm start\"",
    "start": "wrangler dev ./build/index.js --port=8789 --persist-to=../../persistence",
    "typecheck": "tsc"
  },
  "dependencies": {
    "@cloudflare/kv-asset-handler": "^0.1.3",
    "@remix-run/cloudflare": "^2.8.1",
    "@remix-run/css-bundle": "^2.8.1",
    "@remix-run/react": "^2.8.1",
    "idb": "^8.0.0",
    "isbot": "^4.1.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "@cloudflare/workers-types": "^4.20230518.0",
    "@remix-run/dev": "^2.8.1",
    "@types/react": "^18.2.20",
    "@types/react-dom": "^18.2.7",
    "tailwindcss": "^3.4.1",
    "typescript": "^5.1.6",
    "wrangler": "^3.24.0"
  },
  "engines": {
    "node": ">=18.0.0"
  }
}

```

### File: `packages/magic-backup-importer/public/fonts/coolicons.ttf`
```ttf
// ERROR FETCHING FILE: 'utf-8' codec can't decode byte 0x80 in position 7: invalid start byte
```

### File: `packages/magic-backup-importer/public/fonts/coolicons.woff`
```woff
// ERROR FETCHING FILE: 'utf-8' codec can't decode byte 0xf8 in position 10: invalid start byte
```

### File: `packages/magic-backup-importer/public/fonts/whitney-300.woff`
```woff
// ERROR FETCHING FILE: 'utf-8' codec can't decode byte 0xf0 in position 11: invalid continuation byte
```

### File: `packages/magic-backup-importer/public/fonts/whitney-300.woff2`
```woff2
// ERROR FETCHING FILE: 'utf-8' codec can't decode byte 0x94 in position 11: invalid start byte
```

### File: `packages/magic-backup-importer/public/fonts/whitney-400.woff`
```woff
// ERROR FETCHING FILE: 'utf-8' codec can't decode byte 0xd8 in position 11: invalid continuation byte
```

### File: `packages/magic-backup-importer/public/fonts/whitney-400.woff2`
```woff2
// ERROR FETCHING FILE: 'utf-8' codec can't decode byte 0xf8 in position 11: invalid start byte
```

### File: `packages/magic-backup-importer/public/fonts/whitney-500.woff`
```woff
// ERROR FETCHING FILE: 'utf-8' codec can't decode byte 0xc8 in position 11: invalid continuation byte
```

### File: `packages/magic-backup-importer/public/fonts/whitney-500.woff2`
```woff2
// ERROR FETCHING FILE: 'utf-8' codec can't decode byte 0xc8 in position 19: invalid continuation byte
```

### File: `packages/magic-backup-importer/public/fonts/whitney-600.woff`
```woff
// ERROR FETCHING FILE: 'utf-8' codec can't decode byte 0xb4 in position 19: invalid start byte
```

### File: `packages/magic-backup-importer/public/fonts/whitney-600.woff2`
```woff2
// ERROR FETCHING FILE: 'utf-8' codec can't decode byte 0x80 in position 19: invalid start byte
```

### File: `packages/magic-backup-importer/public/fonts/whitney-700.woff`
```woff
// ERROR FETCHING FILE: 'utf-8' codec can't decode byte 0x80 in position 11: invalid start byte
```

### File: `packages/magic-backup-importer/public/fonts/whitney-700.woff2`
```woff2
// ERROR FETCHING FILE: 'utf-8' codec can't decode byte 0x9c in position 19: invalid start byte
```

### File: `packages/magic-backup-importer/remix.config.js`
```js
/** @type {import('@remix-run/dev').AppConfig} */
export default {
  ignoredRouteFiles: ["**/*.css"],
  server: "./server.ts",
  serverConditions: ["workerd", "worker", "browser"],
  serverDependenciesToBundle: [
    // bundle everything except the virtual module for the static content manifest provided by wrangler
    /^(?!.*\b__STATIC_CONTENT_MANIFEST\b).*$/,
  ],
  serverMainFields: ["browser", "module", "main"],
  serverMinify: true,
  serverModuleFormat: "esm",
  serverPlatform: "neutral",
  // appDirectory: "app",
  // assetsBuildDirectory: "public/build",
  // publicPath: "/build/",
  // serverBuildPath: "build/index.js",
};

```

### File: `packages/magic-backup-importer/server.ts`
```ts
import __STATIC_CONTENT_MANIFEST from "__STATIC_CONTENT_MANIFEST";
import { getAssetFromKV } from "@cloudflare/kv-asset-handler";
import type { AppLoadContext } from "@remix-run/cloudflare";
import { createRequestHandler, logDevReady } from "@remix-run/cloudflare";
import * as build from "@remix-run/dev/server-build";

const MANIFEST = JSON.parse(__STATIC_CONTENT_MANIFEST);
const handleRemixRequest = createRequestHandler(build, process.env.NODE_ENV);

if (process.env.NODE_ENV === "development") {
  logDevReady(build);
}

export default {
  async fetch(
    request: Request,
    env: {
      __STATIC_CONTENT: Fetcher;
    },
    ctx: ExecutionContext,
  ): Promise<Response> {
    try {
      const url = new URL(request.url);
      const ttl = url.pathname.startsWith("/build/")
        ? 60 * 60 * 24 * 365 // 1 year
        : 60 * 5; // 5 minutes
      return await getAssetFromKV(
        {
          request,
          waitUntil: ctx.waitUntil.bind(ctx),
        } as FetchEvent,
        {
          ASSET_NAMESPACE: env.__STATIC_CONTENT,
          ASSET_MANIFEST: MANIFEST,
          cacheControl: {
            browserTTL: ttl,
            edgeTTL: ttl,
          },
        },
      );
    } catch {
      // No-op
    }

    try {
      const loadContext: AppLoadContext = {
        env,
      };
      return await handleRemixRequest(request, loadContext);
    } catch (error) {
      console.log(error);
      return new Response("An unexpected error occurred", { status: 500 });
    }
  },
};

```

### File: `packages/magic-backup-importer/tailwind.config.ts`
```ts
import type { Config } from "tailwindcss";

export default {
  content: ["./app/**/*.{js,ts,jsx,tsx}"],
  theme: {
    fontFamily: {
      sans: ["Whitney", "Helvetica", "sans-serif"],
    },
    extend: {
      colors: {
        brand: {
          blue: "#58B9FF",
          pink: "#FF81FF",
        },
        primary: {
          130: "#EFF0F3",
          200: "#E3E5E8",
          230: "#DBDEE1",
          600: "#313338",
          630: "#202225",
          700: "#17181A",
        },
        blurple: {
          50: "#eef3ff",
          100: "#e0e9ff",
          200: "#c6d6ff",
          300: "#a4b9fd",
          400: "#8093f9",
          DEFAULT: "#5865f2",
          500: "#5865f2",
          600: "#4654c0",
          700: "#3a48a3",
          800: "#2f2fa4",
          900: "#2d2f82",
          950: "#1a1a4c",
        },
        gray: {
          100: "#f2f3f5",
          200: "#ebedef",
          300: "#e3e5e8",
          400: "#d4d7dc",
          600: "#4f545c",
          700: "#36393f",
          800: "#2f3136",
          900: "#202225",
        },
      },
    },
  },
  plugins: [],
} satisfies Config;

```

### File: `packages/magic-backup-importer/tsconfig.json`
```json
{
  "include": ["remix.env.d.ts", "**/*.ts", "**/*.tsx"],
  "compilerOptions": {
    "lib": ["DOM", "DOM.Iterable", "ES2022"],
    "isolatedModules": true,
    "esModuleInterop": true,
    "jsx": "react-jsx",
    "moduleResolution": "Bundler",
    "resolveJsonModule": true,
    "target": "ES2022",
    "strict": true,
    "allowJs": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "baseUrl": ".",
    "paths": {
      "~/*": ["./app/*"]
    },

    // Remix takes care of building everything in `remix build`.
    "noEmit": true
  }
}

```

### File: `packages/magic-backup-importer/wrangler.toml`
```toml
name = "discohook-backup-importer"
main = "./build/index.js"
compatibility_date = "2023-04-20"

[site]
  bucket = "./public"

[build]
  command = "npm run build"

[vars]
DISCOHOOK_ORIGIN = "https://discohook.app"

[env.preview]
name = "discohook-backup-importer-preview"

[env.preview.vars]
DISCOHOOK_ORIGIN = "https://preview.discohook.app"

[env.production.vars]
DISCOHOOK_ORIGIN = "https://discohook.app"

```

